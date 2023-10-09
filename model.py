from fastai.vision.all import *

# Define paths to your data
path = Path("/Users/julianbaumgartner/dev/MrPloops/imgs")

# Create DataLoaders
data = ImageDataLoaders.from_folder(
    path,
    train=".",
    valid_pct=0.2,
    item_tfms=Resize(460),
    batch_tfms=[*aug_transforms(size=224), Normalize.from_stats(*imagenet_stats)],
)

# Create a CNN learner
learn = cnn_learner(data, resnet34, metrics=accuracy)

# Find a suitable learning rate
lr_min, lr_steep = learn.lr_find()

# Train the model
learn.fine_tune(epochs=5, base_lr=lr_min)

# Evaluate the model
interp = ClassificationInterpretation.from_learner(learn)
interp.plot_confusion_matrix()
