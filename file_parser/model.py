from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Embedding, LSTM, Concatenate, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from file_parser.create_dataset import *
from file_parser.train_model import *

class SentenceSplitter():
    def __init__(self,
            sentence_length,
            lstm_layers_size,
            embedding_layer_size,
            dropout_rate,
            activation,
            epochs
    ):
        super().__init__()
        self.sentence_length = sentence_length
        self.lstm_layers_size = lstm_layers_size
        self.embedding_layer_size = embedding_layer_size
        self.dropout_rate = dropout_rate
        self.activation = activation
        self.epochs = epochs

    def sent2seq(self, sentence, padding_location="pre"):
        sequences = self.tokenizer.texts_to_sequences([sentence])
        return pad_sequences(sequences, maxlen=self.sentence_length, dtype='int32', padding=padding_location,
            truncating=padding_location, value=0.0).squeeze()

    def read_dataset(self, texts):
      positives_pairs, negative_pairs = create_dataset(texts)
      self.tokenizer = Tokenizer()

      corpus = [[nltk.tokenize.word_tokenize(sentence) for sentence in nltk.sent_tokenize(text)] for text in texts]
      corpus =list(chain.from_iterable(corpus)) 
      self.tokenizer.fit_on_texts(corpus)

      positives_pairs = np.array([[self.sent2seq(sent1, padding_location="pre"),
                                    self.sent2seq(sent2, padding_location="post")] for sent1, sent2 in
                                  positives_pairs])
      negative_pairs = np.array([[self.sent2seq(sent1, padding_location="pre"),
                                  self.sent2seq(sent2, padding_location="post")] for sent1, sent2 in negative_pairs])
      
      X = np.concatenate((positives_pairs, negative_pairs))
      y = np.array([1] * len(positives_pairs) + [0] * len(negative_pairs))
      return X, y

    def fit(self, X, y):
        '''
        X: sentences pairs
        y: 1- represent splitted sentences, 0- represent merged sentences
        '''
        weights = y * (len(y) - sum(y)) / sum(y)  # positive weight
        weights[weights == 0] = 1  # negative weight
        logging.info(f"Number of positives: {len(y[y == 1])}, Number of negatives: {len(y[y == 0])}")
        vocab_size = len(self.tokenizer.word_index) + 1

        # first sentence forward
        forward_model_input = Input(shape=(X.shape[-1],))
        forward_model = Embedding(vocab_size, self.embedding_layer_size)(forward_model_input)
        forward_model = self.add_lstm_layers(forward_model, go_backwards=False)

        # second sentence backward
        backward_model_input = Input(shape=(X.shape[-1],))
        backward_model = Embedding(vocab_size, self.embedding_layer_size)(backward_model_input)
        backward_model = self.add_lstm_layers(backward_model, go_backwards=True)

        model_concatenated = Concatenate()([forward_model, backward_model])
        model_concatenated = Dense(self.lstm_layers_size[-1] * 2, activation=self.activation)(model_concatenated)

        model_concatenated = Dense(1, activation='sigmoid')(model_concatenated)
        self.model = Model(inputs=[forward_model_input, backward_model_input], outputs=model_concatenated)

        logging.info(f"Dataset shape: {X.shape}")
        self.model.summary(print_fn=logging.getLogger(__name__).info)

        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.fit([X[:, 0, :], X[:, 1, :]], y, batch_size=256, epochs=self.epochs, shuffle=True,
            sample_weight=weights)

    def add_lstm_layers(self, model, go_backwards=False):
        for i, layer_dim in enumerate(self.lstm_layers_size):
            if i == len(self.lstm_layers_size) - 1:  # last layer
                model = LSTM(layer_dim, return_sequences=False, dropout=self.dropout_rate,
                    go_backwards=go_backwards)(model)
            else:
                model = LSTM(layer_dim, return_sequences=True, dropout=self.dropout_rate,
                    go_backwards=go_backwards)(model)
        return model

    def transform(self, sentences):
        if len(sentences) == 0:
            return []
        splitted_sentences = [sentences[0]]
        for sentence in sentences[1:]:
            previous_sentence = splitted_sentences.pop()
            pair_sentences = np.array([self.sent2seq(nltk.tokenize.word_tokenize(previous_sentence), padding_location="pre"),
                                       self.sent2seq(nltk.tokenize.word_tokenize(sentence), padding_location="post")])

            prob_split= self.model.predict([pair_sentences[0, :].reshape(1, self.sentence_length),
                                                 pair_sentences[1, :].reshape(1, self.sentence_length)])[:, 0][0]
            if prob_split > 0.5:
                splitted_sentences += [previous_sentence, sentence]
            else: #merge
                splitted_sentences += [(previous_sentence + ' ' + sentence)]

        return splitted_sentences


if __name__ == "__main__":
  model = SentenceSplitter(sentence_length=80,
            lstm_layers_size= (64, 32),
            embedding_layer_size = 100,
            dropout_rate= 0.3,
            activation= 'softmax',
            epochs=10)
  X, y = model.read_dataset("The modern Olympic Games or Olympics are leading international sporting events", 
                       "featuring summer and winter sports competitions in which", 
                       "thousands of athletes from around the world participate in a variety of competitions")
  model.fit(X,y)
  model.transform(["The modern Olympic Games or Olympics are leading international sporting events", 
                       "featuring summer and winter sports competitions in which", 
                       "thousands of athletes from around the world participate in a variety of competitions"])
