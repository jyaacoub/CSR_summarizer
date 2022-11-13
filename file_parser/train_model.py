from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Embedding, LSTM, Concatenate, Dense

lstm_layer_size= 64
embedding_layer_size = 100
dropout_rate= 0.3
activation= 'softmax'
epochs=10

weights = y * (len(y) - sum(y)) / sum(y)  # positive weight
weights[weights == 0] = 1  # negative weight
vocab_size = len(tokenizer.word_index) + 1

# first sentence forward
forward_model_input = Input(shape=(X.shape[-1],))
forward_model = Embedding(vocab_size, embedding_layer_size)(forward_model_input)
forward_model = LSTM(lstm_layer_size, return_sequences=False, dropout=dropout_rate,
            go_backwards=False)(forward_model)

# second sentence backward
backward_model_input = Input(shape=(X.shape[-1],))
backward_model = Embedding(vocab_size, embedding_layer_size)(backward_model_input)
backward_model = LSTM(lstm_layer_size, return_sequences=False, dropout=dropout_rate,
            go_backwards=True)(backward_model)

model_concatenated = Concatenate()([forward_model, backward_model])
model_concatenated = Dense(lstm_layer_size * 2, activation=activation)(model_concatenated)

model_concatenated = Dense(1, activation='sigmoid')(model_concatenated)
model = Model(inputs=[forward_model_input, backward_model_input], outputs=model_concatenated)

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit([X[:, 0, :], X[:, 1, :]], y, batch_size=256, epochs=epochs, shuffle=True,
    sample_weight=weights)