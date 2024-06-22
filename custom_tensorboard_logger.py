import os
from datetime import datetime
import logging

# Import Rasa dependencies
from rasa.model_training import train
from rasa.shared.nlu.training_data.loading import load_data

# Import TensorFlow
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard

# Import your custom tokenizer
from custom import ThaiTokenizer

# Set up logging to terminal
logging.basicConfig(level=logging.INFO)

# Path to save TensorBoard logs
log_dir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
os.makedirs(log_dir, exist_ok=True)

# Train the model and log training information
def train_and_log():
    # Load NLU training data
    nlu_data = load_data("data/nlu.yml")

    # Tokenization and text vectorization
    tokenizer = ThaiTokenizer(config={})
    tokenized_data = tokenizer.tokenize(nlu_data,attribute="Text")

    # Convert tokenized data into numerical vectors
    numerical_data = vectorize_data(tokenized_data)

    # Pad sequences to ensure uniform length
    padded_data = pad_sequences(numerical_data)

    # Split the data into input features and target labels
    X = padded_data[:, :-1]
    y = padded_data[:, -1]

    # Define model architecture (example using TED policy)
    model = tf.keras.Sequential([
        # Define your model layers here
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Create a TensorBoard callback
    tensorboard_callback = TensorBoard(log_dir=log_dir)

    # Train the model with TensorBoard callback
    model.fit(
        x=X,
        y=y,
        epochs=10,  # Adjust as needed
        callbacks=[tensorboard_callback]  # Add TensorBoard callback to the training process
    )

    # Save the trained model
    model.save("models")

    # Log completion message
    completion_message = "Training completed successfully."
    logging.info(completion_message)


if __name__ == "__main__":
    train_and_log()
