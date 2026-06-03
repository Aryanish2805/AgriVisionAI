print("This project has been updated to AI-Based Crop Recommendation System Using Machine Learning.")
print("Use recommend.py or the Streamlit app in frontend/app.py instead of detect.py.")


def find_sample_image(root: Path) -> Path | None:
    if not root.exists():
        return None
    for class_dir in sorted(root.iterdir()):
        if class_dir.is_dir():
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG"]:
                images = list(class_dir.glob(ext))
                if images:
                    return images[0]
    return None


def main():
    sample_image = find_sample_image(DATASET_ROOT)
    if sample_image is None:
        print("No sample image found in dataset. Make sure the dataset is extracted to:")
        print(DATASET_ROOT)
        return

    model = YOLO(MODEL_PATH)

    print("Running detection on:", sample_image)
    model.predict(source=str(sample_image), save=True)
    print("Detection complete. Results saved under runs/detect/predict")


if __name__ == "__main__":
    main()