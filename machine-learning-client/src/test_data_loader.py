from data import get_train_loader, get_test_loader

def main():
    train_loader = get_train_loader()
    test_loader = get_test_loader()

    print("Train loader created successfully.")
    print("Test loader created successfully.")

    train_images, train_labels = next(iter(train_loader))
    test_images, test_labels = next(iter(test_loader))

    print("Train batch image shape:", train_images.shape)
    print("Train batch label shape:", train_labels.shape)
    print("First 10 train labels:", train_labels[:10])

    print("Test batch image shape:", test_images.shape)
    print("Test batch label shape:", test_labels.shape)
    print("First 10 test labels:", test_labels[:10])

    image, label = train_loader.dataset[0]
    print("Single image shape:", image.shape)
    print("Single label:", label)
    print("Image min/max:", image.min().item(), image.max().item())

if __name__ == "__main__":
    main()