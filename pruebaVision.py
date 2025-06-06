import cv2
import numpy as np

# --- 1. Predefined Puzzle Information ---
FULL_PUZZLE_PATH = 'PuzleAzulCOMPLETO.jpg'

POSITION_MAP = {
    (0, 0): 1, (0, 1): 2, (0, 2): 3,
    (1, 0): 4, (1, 1): 5, (1, 2): 6,
    (2, 0): 7, (2, 1): 8, (2, 2): 9
}

# --- Helper Functions (defined before they are called) ---

def load_and_preprocess_image(image_path_or_frame, is_puzzle_piece=False):
    """
    Loads an image (from path or camera frame) and applies basic preprocessing.
    If is_puzzle_piece is True, it attempts to crop the main square object.
    """
    if isinstance(image_path_or_frame, str):
        img = cv2.imread(image_path_or_frame)
    else: # Assume it's a webcam frame (numpy array)
        img = image_path_or_frame

    if img is None:
        print(f"Error: Could not load image or frame.")
        return None, None

    original_color_img = img.copy() # Keep a copy of the original color image

    # Convert to grayscale for most processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if is_puzzle_piece:
        cv2.imshow('DEBUG: Preprocess - Gray Image', gray) # DEBUG
        cv2.waitKey(1) # DEBUG

    # Optional: Apply Gaussian blur to reduce noise (can be tuned)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0) # Changed to 3x3
    if is_puzzle_piece:
        cv2.imshow('DEBUG: Preprocess - Blurred Image', blurred) # DEBUG
        cv2.waitKey(1) # DEBUG

    # Using blurred for now, you can uncomment equalizeHist if you want to try it.
    # equalized = cv2.equalizeHist(blurred)
    # processed_gray = equalized
    processed_gray = blurred

    # If it's an individual piece from the webcam, try to crop it from the background
    if is_puzzle_piece:
        print(f"  [DEBUG load_and_preprocess_image] Processing for piece cropping. Shape: {processed_gray.shape}, min/max: {processed_gray.min()}/{processed_gray.max()}")
        
        # Using a threshold to isolate the piece from the typically brighter background
        # You might need to tune the threshold value (e.g., 200) based on your lighting
        _, thresh = cv2.threshold(processed_gray, 200, 255, cv2.THRESH_BINARY_INV) # Adjust threshold if background isn't pure white
        
        cv2.imshow('DEBUG: Preprocess - Thresholded Image', thresh) # DEBUG
        cv2.waitKey(0) # DEBUG: Use 0 to pause and inspect this image. Close it to continue.

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("  [DEBUG load_and_preprocess_image] Warning: No contours found for piece. Cropping might fail.")
            # If no contours are found, we'll return the uncropped processed image and original.
            # This allows the program to continue, but the feature detection might be less accurate
            # if the background is still present.
            return processed_gray, original_color_img

        # Find the largest contour (likely the puzzle piece)
        largest_contour = max(contours, key=cv2.contourArea)
        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Add some padding to the bounding box if desired
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2 * padding)
        h = min(img.shape[0] - y, h + 2 * padding)

        # Ensure the crop coordinates are valid before slicing
        if x + w > img.shape[1] or y + h > img.shape[0] or w <= 0 or h <= 0:
            print(f"  [DEBUG load_and_preprocess_image] Warning: Invalid crop coordinates detected. Returning uncropped image. Bbox: ({x},{y},{w},{h}), Img Shape: {img.shape}")
            return processed_gray, original_color_img


        # Crop the image using the bounding box
        processed_gray = processed_gray[y:y+h, x:x+w]
        original_color_img = original_color_img[y:y+h, x:x+w]
        
        print(f"  [DEBUG load_and_preprocess_image] Image successfully cropped. New shape: {processed_gray.shape}")

    # Ensure processed_gray is not empty after potential cropping
    if processed_gray.shape[0] == 0 or processed_gray.shape[1] == 0:
        print("  [DEBUG load_and_preprocess_image] Warning: Processed image is empty after all steps.")
        return None, None

    return processed_gray, original_color_img

def segment_full_puzzle(full_puzzle_img_gray):
    """
    Segments the full 3x3 puzzle image into 9 individual piece regions.
    This assumes a flat surface and that the puzzle pieces are roughly aligned in a grid.
    """
    h, w = full_puzzle_img_gray.shape
    piece_width = w // 3
    piece_height = h // 3

    puzzle_pieces = []
    for r in range(3):
        for c in range(3):
            y1 = r * piece_height
            y2 = (r + 1) * piece_height
            x1 = c * piece_width
            x2 = (c + 1) * piece_width
            piece = full_puzzle_img_gray[y1:y2, x1:x2]
            puzzle_pieces.append((piece, (r, c)))

    return puzzle_pieces

def extract_features(image):
    """
    Extracts features from an image using ORB (Oriented FAST and Rotated BRIEF).
    Returns keypoints and descriptors.
    """
    # Input validation
    if image is None or image.shape[0] == 0 or image.shape[1] == 0:
        print("  [DEBUG extract_features] Warning: Received empty or invalid image for feature extraction.")
        return None, None

    orb = cv2.ORB_create(nfeatures=1000) # Increased features to try and capture subtle details
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def compare_features(piece_desc, puzzle_piece_desc):
    """
    Compares the descriptors of the input piece with a segmented puzzle piece.
    Uses Brute-Force Matcher with k-NN (k-Nearest Neighbors) matching.
    Adjusted for ORB descriptors.
    """
    # Need at least 2 descriptors for knnMatch with k=2
    if piece_desc is None or puzzle_piece_desc is None or len(piece_desc) < 2 or len(puzzle_piece_desc) < 2:
        return 0

    # For ORB (binary descriptors), use FLANN_INDEX_LSH
    FLANN_INDEX_LSH = 6
    index_params= dict(algorithm = FLANN_INDEX_LSH,
                       table_number = 6, # Typical values 6, 12
                       key_size = 12,     # Typical values 12, 20
                       multi_probe_level = 1) # Typical values 1, 2
    search_params = dict(checks=50) # Number of times the trees should be recursively traversed

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    try:
        matches = flann.knnMatch(piece_desc, puzzle_piece_desc, k=2)
    except cv2.error as e:
        print(f"  [DEBUG compare_features] FLANN matching error: {e}. Descriptors might be empty or invalid. Skipping this match.")
        return 0

    good_matches = []
    # Apply ratio test to find good matches (Lowe's ratio test)
    # A ratio of 0.75 is often a good compromise.
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    return len(good_matches) # Return the number of good matches as a similarity score

def find_puzzle_piece_position(input_piece_frame, full_puzzle_img_path):
    """
    Main function to find the position of the input piece in the full puzzle.
    """
    # 1. Preprocess the input piece image (with cropping from its background)
    input_piece_gray, input_piece_original_cropped = load_and_preprocess_image(input_piece_frame, is_puzzle_piece=True)
    if input_piece_gray is None:
        return "Error: Input image processing failed (could not load or crop).", None, None

    # 2. Preprocess the full puzzle image
    full_puzzle_gray, full_puzzle_original = load_and_preprocess_image(full_puzzle_img_path, is_puzzle_piece=False)
    if full_puzzle_gray is None:
        return "Error: Full puzzle image processing failed (could not load).", None, None

    segmented_puzzle_pieces_gray = segment_full_puzzle(full_puzzle_gray)
    
    # Extract color segments from the original full puzzle image for drawing matches later
    full_puzzle_color_segments = [
        full_puzzle_original[
            r * (full_puzzle_original.shape[0] // 3) : (r + 1) * (full_puzzle_original.shape[0] // 3),
            c * (full_puzzle_original.shape[1] // 3) : (c + 1) * (full_puzzle_original.shape[1] // 3)
        ] for _, (r, c) in segmented_puzzle_pieces_gray
    ]

    # 3. Extract features from the input piece
    kp_input, desc_input = extract_features(input_piece_gray)
    if desc_input is None or len(kp_input) < 2: # Require at least 2 keypoints for matching
        print(f"  [Debug] Input piece: No sufficient features detected. Keypoints: {len(kp_input) if kp_input else 0}")
        # Show the processed input piece so you can see if cropping worked correctly
        cv2.imshow('Processed Input Piece (Insufficient Features)', input_piece_gray)
        cv2.waitKey(1) # Display briefly
        return "No sufficient features detected in the input piece. Try adjusting lighting or focus.", input_piece_original_cropped, None

    best_match_score = -1
    matched_position = None
    matched_piece_image_color = None
    best_matches_list = [] # To store the actual matches for drawing

    print(f"\n  [Debug] Comparing input piece (KPs: {len(kp_input)}) against all puzzle pieces:")
    # 4. Iterate through segmented puzzle pieces and compare
    for i, (segmented_piece_gray, (r, c)) in enumerate(segmented_puzzle_pieces_gray):
        kp_puzzle, desc_puzzle = extract_features(segmented_piece_gray)
        if desc_puzzle is None or len(kp_puzzle) < 2: # Require at least 2 keypoints
            print(f"    [Debug] Piece ({r},{c}): Insufficient features. KPs: {len(kp_puzzle) if kp_puzzle else 0}. Skipping.")
            continue

        match_score = compare_features(desc_input, desc_puzzle)
        print(f"    [Debug] Score for piece ({r},{c}) (KPs: {len(kp_puzzle)}): {match_score}") # Detailed score print

        if match_score > best_match_score:
            best_match_score = match_score
            matched_position = (r, c)
            matched_piece_image_color = full_puzzle_color_segments[i] # Get the color version for drawing matches

            # Re-run matching to get the actual matches for visualization with the best score
            # This is slightly redundant but ensures we have the `matches` object for `drawMatches`
            FLANN_INDEX_LSH = 6
            index_params= dict(algorithm = FLANN_INDEX_LSH, table_number = 6, key_size = 12, multi_probe_level = 1)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            try:
                temp_matches = flann.knnMatch(desc_input, desc_puzzle, k=2)
                best_matches_list = [m for m, n in temp_matches if m.distance < 0.75 * n.distance]
            except cv2.error:
                best_matches_list = [] # Reset if error occurs

    print(f"\n  [Debug] Best match score found: {best_match_score} at position {matched_position}")

    # 5. Determine if it's a match and assign position number
    # This threshold is CRUCIAL and needs tuning based on observed 'best_match_score' values.
    # Start low and increase until false positives disappear.
    MATCH_THRESHOLD = 15 # Suggested starting point, adjust as needed!

    if best_match_score > MATCH_THRESHOLD and matched_position is not None:
        position_number = POSITION_MAP[matched_position]
        
        # Draw matches for visualization only if we have keypoints and matches
        if kp_input is not None and kp_puzzle is not None and best_matches_list:
            img_matches = cv2.drawMatches(input_piece_original_cropped, kp_input,
                                          matched_piece_image_color, kp_puzzle,
                                          best_matches_list, None,
                                          flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow("Good Matches Found", img_matches)
            cv2.waitKey(1) # Show briefly
        else:
            print("  [Debug] Warning: Could not draw matches due to missing keypoints or matches list.")

        return f"La pieza corresponde a la posición: {matched_position}, número: {position_number}", input_piece_original_cropped, matched_piece_image_color
    else:
        print(f"  [Debug] No match found above the set threshold ({MATCH_THRESHOLD}).")
        return "No corresponde al puzle", input_piece_original_cropped, None

# --- Main Program Execution ---
if __name__ == "__main__":
    # --- Part 1: Load and Display Full Puzzle ---
    full_puzzle_img_path = FULL_PUZZLE_PATH

    # Load the full puzzle image
    full_puzzle_original_loaded = cv2.imread(full_puzzle_img_path)

    # Check if the full puzzle image was loaded successfully
    if full_puzzle_original_loaded is None:
        print(f"Error: Could not load the full puzzle image at '{full_puzzle_img_path}'.")
        print("Creating a dummy 'PuzleAzulCOMPLETO.jpg' for demonstration if not found.")
        dummy_img = np.zeros((300, 300, 3), dtype=np.uint8)
        # Draw some simple "puzzle pieces" with different colors/patterns
        cv2.rectangle(dummy_img, (0,0), (100,100), (255,0,0), -1) # Red top-left
        cv2.rectangle(dummy_img, (100,0), (200,100), (0,255,0), -1) # Green top-middle
        cv2.rectangle(dummy_img, (200,0), (300,100), (0,0,255), -1) # Blue top-right
        cv2.rectangle(dummy_img, (0,100), (100,200), (255,255,0), -1) # Yellow middle-left
        cv2.rectangle(dummy_img, (100,100), (200,200), (255,0,255), -1) # Magenta center
        cv2.rectangle(dummy_img, (200,100), (300,200), (0,255,255), -1) # Cyan middle-right
        cv2.rectangle(dummy_img, (0,200), (100,300), (128,128,128), -1) # Gray bottom-left
        cv2.rectangle(dummy_img, (100,200), (200,300), (0,0,0), -1) # Black bottom-middle
        cv2.rectangle(dummy_img, (200,200), (300,300), (255,255,255), -1) # White bottom-right
        cv2.imwrite(full_puzzle_img_path, dummy_img)
        print("Dummy 'PuzleAzulCOMPLETO.jpg' created.")
        full_puzzle_original_loaded = cv2.imread(full_puzzle_img_path) # Try loading again

    # Display the full puzzle image
    if full_puzzle_original_loaded is not None:
        cv2.imshow('Full Puzzle for Comparison', full_puzzle_original_loaded)
        cv2.waitKey(1) # Display for a moment, then continue to the next part

    # --- Part 2: Process Input Pieces (Static Images for testing) ---
    test_input_images = {
        "1_2.jpg": "should be recognized (Bluey's head)",
        "1_1.jpg": "should be (0,0) (Bluey's foot)"
    }

    for img_file, description in test_input_images.items():
        print(f"\n--- Testing with '{img_file}' ({description}) ---")
        input_piece_static_frame = cv2.imread(img_file, cv2.IMREAD_COLOR)

        if input_piece_static_frame is None:
            print(f"Error: Could not load the input image '{img_file}'. Please ensure it exists.")
            continue # Skip to the next test image

        # Call the main detection function
        result_message, input_piece_display, matched_piece_img_display = find_puzzle_piece_position(
            input_piece_static_frame, full_puzzle_img_path
        )
        print(f"Result for '{img_file}': {result_message}")

        # Display results for current test image
        if input_piece_display is not None:
            cv2.imshow(f'Input Piece (Cropped) - {img_file}', input_piece_display)
        
        if matched_piece_img_display is not None:
            cv2.imshow(f'Matched Piece from Full Puzzle - {img_file}', matched_piece_img_display)
        
        print("\nPress any key to process the next image (or close all windows for final exit).")
        cv2.waitKey(0) # Wait indefinitely until a key is pressed to close the result windows for this image
        cv2.destroyWindow(f'Input Piece (Cropped) - {img_file}')
        if matched_piece_img_display is not None:
            cv2.destroyWindow(f'Matched Piece from Full Puzzle - {img_file}')
        cv2.destroyWindow('Good Matches Found') # Close if it was opened
        cv2.destroyWindow('Processed Input Piece (Insufficient Features)') # Close if it was opened


    print("\n--- All Static Image Tests Complete ---")
    print("Check the console output for match scores and messages.")
    print("Close any remaining windows to exit.")
    
    cv2.waitKey(0) # Final wait for any lingering windows
    cv2.destroyAllWindows()

    # --- How to switch to live webcam input (uncomment these lines and comment out the "Part 2" static image section) ---
    # print("\n--- Switching to Webcam Mode ---")
    # cap = cv2.VideoCapture(0) # 0 is typically the default webcam
    # if not cap.isOpened():
    #     print("Error: Could not open webcam.")
    #     exit()
    # print("\nPress 'q' to quit webcam feed.")
    # print("Press 'c' to capture a piece and compare from webcam.")
    # while True:
    #     ret, frame = cap.read() # Read a frame from the webcam
    #     if not ret:
    #         print("Failed to grab frame.")
    #         break
    #     cv2.imshow('Webcam Feed (Press "c" to capture and compare)', frame)
    #     key = cv2.waitKey(1) & 0xFF
    #     if key == ord('q'):
    #         break
    #     elif key == ord('c'):
    #         print("Capturing frame for comparison...")
    #         result_message, input_piece_display, matched_piece_img_display = find_puzzle_piece_position(frame, full_puzzle_img_path)
    #         print(result_message)
    #         if input_piece_display is not None:
    #             cv2.imshow('Input Piece (Cropped and Processed)', input_piece_display)
    #         if matched_piece_img_display is not None:
    #             cv2.imshow('Matched Piece from Full Puzzle', matched_piece_img_display)
    #         cv2.waitKey(0) # Wait indefinitely until a key is pressed to close result windows
    #         cv2.destroyWindow('Good Matches Found') # Close if it was opened
    #         cv2.destroyWindow('Input Piece (Cropped and Processed)')
    #         cv2.destroyWindow('Matched Piece from Full Puzzle')
    #         cv2.destroyWindow('Processed Input Piece (Insufficient Features)')
    # cap.release()
    # cv2.destroyAllWindows()