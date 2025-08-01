---
title: "AI Sign Language Interpreter"
date: 2025-04-07
description: "A Simple Sign Language Recognition App using OpenCV"
tags: ["python", "sign language", "machine learning"]
categories: ["Projects"]
draft: false
---

[GitHub Repo](https://github.com/loyolaaiclub/Sign-Language-Recognition)

Over the course of the early Spring Semester, I lead the Loyola AI Club's project to create a sign language 
interpreter. The original goal of the project was to download a ton of sign language videos from a dataset and see if we could create a working sign language interpreter using OpenCV and Python. 

The process was as follows:

1. Use a [list of YouTube links from Microsoft](https://github.com/loyolaaiclub/Sign-Language-Recognition/blob/8be753d802f3424ba300037bf7bb17334a498997/MS-ASL/MSASL_val.json) that would show ASL in action along with a label of the sign. In this case the training and testing data was split for us already.
2. Download the videos and then convert those downloaded videos to a convenient format for machine learning using [this script](https://github.com/loyolaaiclub/Sign-Language-Recognition/blob/8be753d802f3424ba300037bf7bb17334a498997/json_process.py). 

```
def download_youtube_video(url, videos_folder=VIDEOS_FOLDER):
    """Download a YouTube video using yt-dlp and return the local file path."""
    video_id = get_video_id(url)
    filename = f"{video_id}.mp4"
    video_path = os.path.join(videos_folder, filename)
    if os.path.exists(video_path):
        print(f"[INFO] Video already exists: {video_path}")
        return video_path
    try:
        print(f"[INFO] Downloading video {url} ...")
        command = [
            "yt-dlp",
            "--no-check-certificate",
            "-f", "mp4",
            "-o", video_path,
            url
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] yt-dlp failed: {result.stderr}")
            return None
        print(f"[INFO] Video saved as {video_path}")
        return video_path
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")
        return None
```

3. From our new dataset, we could train the similarities between the images and labels. [link](https://github.com/loyolaaiclub/Sign-Language-Recognition/blob/8be753d802f3424ba300037bf7bb17334a498997/json_training.py)

```
def main():
    # Load data from processed NPZ files
    X, y = load_npz_data(DATA_FOLDER)
    print(f"[INFO] Loaded {len(X)} samples.")

    if len(X) == 0:
        print("[ERROR] No data loaded. Exiting.")
        return

    # Build a label-to-index mapping based on the gesture folder names
    unique_labels = sorted(list(set(y)))
    label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
    print(f"[INFO] Found {len(unique_labels)} unique gesture classes: {unique_labels}")

    # Convert string labels to integer indices and then to one-hot vectors
    y_indices = np.array([label_to_index[label] for label in y])
    num_classes = len(unique_labels)
    y_cat = to_categorical(y_indices, num_classes)

    # Build a simple Conv3D model
    model = Sequential([
        Conv3D(32, (3, 3, 3), activation="relu", input_shape=(NUM_FRAMES, IMG_SIZE[0], IMG_SIZE[1], 1)),
        MaxPooling3D(pool_size=(1, 2, 2)),
        Conv3D(64, (3, 3, 3), activation="relu"),
        MaxPooling3D(pool_size=(1, 2, 2)),
        Dropout(0.3),
        Flatten(),
        Dense(128, activation="relu"),
        Dropout(0.5),
        Dense(num_classes, activation="softmax")
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    model.summary()

    steps_per_epoch = max(1, len(X) // BATCH_SIZE)

    # Set up callbacks: checkpointing and early stopping
    checkpoint_callback = ModelCheckpoint(
        filepath="model_checkpoint.h5",
        monitor="loss",
        save_best_only=True,
        verbose=1
    )
    early_stopping_callback = EarlyStopping(
        monitor="loss",
        patience=5,
        verbose=1
    )

    # Train the model using the data generator (with augmentation)
    model.fit(
        data_generator(X, y_cat, batch_size=BATCH_SIZE, augment=True),
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS,
        callbacks=[checkpoint_callback, early_stopping_callback]
    )

    model.save("asl_model.h5")
    print("[INFO] Model saved as asl_model.h5")
```

4. Finally, our model would be tested with a live camera. [link](https://github.com/loyolaaiclub/Sign-Language-Recognition/blob/8be753d802f3424ba300037bf7bb17334a498997/app_json.py#L24)

```
# Process the frame with MediaPipe for hand detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands_detector.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            else:
                cv2.putText(frame, "No hand detected", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
```

5. Once the model could consistently recognize a piece from the dataset, I would use this approach and phase-2 it into pairing an LLM to interpret the sign language as a sentence. Thereby, providing live translation of sign language in the form of text.

Now, we had some issues with this approach. Our data was set in .npz format which was great for storage but not great for training. Additionally, the videos being downloaded put a strain on my local wifi network--which before I took on this project was assumed to be unlimited--I did not know you could run out of wifi. So, I thank Loyola's wifi network for handling the rest of the data transfer.

The second approach was to use mediapipe to overlay on our original videos and transform them into csv dot arrays. I thought this approach was smart but it ultimately did not end up working. And, due to the time to train and download, I resorted to a simpler approach for the app.

As a cop out, I used an existing model of a single letter ASL interpreter. This could handle 26 letters and one hand. 

```
def preprocess_hand_image(hand_img):
    """Preprocess the hand image for the model"""
    if hand_img.size == 0:
        return None
        
    # Convert to grayscale and resize
    hand_gray = cv2.cvtColor(hand_img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive histogram equalization for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    hand_eq = clahe.apply(hand_gray)
    
    # Resize to model input size
    hand_resized = cv2.resize(hand_eq, (28, 28))
    
    # Normalize and reshape for model input
    processed = hand_resized.astype('float32') / 255.0
    processed = np.expand_dims(processed, axis=(0, -1))
    return processed, hand_resized
```

Regardless, it was a very fun top to bottom project working with data processing and a little bit of machine learning. 

Also, very fun fact about my website is that it's exactly copied from the Loyola AI Club's website. See [here](https://loyolaaiclub.github.io/projects/movierec/)