import json
import pickle
import random
import string
import nltk
import numpy as np
import tensorflow as tf
from keras.layers import Dense, Dropout
from keras.models import Sequential
from nltk.stem import WordNetLemmatizer


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


def train_bot():
    # Loading intent json file
    with open('intents.json') as intents:
        data = json.load(intents)

    # Loading timetable json file
    with open('timetable.json') as timetable:
        timetable_data = json.load(timetable)

    # Loading events json file
    with open('event.json') as events:
        events_data = json.load(events)

    # Loading lecturer json file
    with open('lecturer.json') as lecturer:
        lecturer_data = json.load(lecturer)

    # Initializing chatbot training
    words = []
    classes = []
    data_x = []
    data_y = []

    # Collecting data from intents.json
    for intent in data['intents']:
        for pattern in intent['patterns']:
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            data_x.append(pattern)
            data_y.append(intent['tag'])

            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # Collecting data from timetable.json
    for timetable in timetable_data['intents']:
        for pattern in timetable['patterns']:
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            data_x.append(pattern)
            data_y.append(timetable['tag'])

            if timetable['tag'] not in classes:
                classes.append(timetable['tag'])

    # Collecting data from events.json
    for events in events_data['intents']:
        for pattern in events['patterns']:
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            data_x.append(pattern)
            data_y.append(events['tag'])

            if events['tag'] not in classes:
                classes.append(events['tag'])

    # Collecting data from lecturer.json
    for lecturer in lecturer_data['intents']:
        for pattern in lecturer['patterns']:
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            data_x.append(pattern)
            data_y.append(lecturer['tag'])

            if lecturer['tag'] not in classes:
                classes.append(lecturer['tag'])

    # Merging the intents from all files
    data['intents'] += timetable_data['intents']
    data['intents'] += events_data['intents']
    data['intents'] += lecturer_data['intents']

    # Initializing lemmatizer to get stem of words
    lemmatizer = WordNetLemmatizer()

    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in string.punctuation]
    words = sorted(list(set(words)))

    classes = sorted(list(set(classes)))

    print(len(data_x), "data_X")
    print(len(data_y), "data_Y")
    print(len(classes), "classes", classes)
    print(len(words), "unique lemmatized words", words)

    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))

    training = []
    output_empty = [0] * len(classes)

    # Creating Bag of Words
    for idx, doc in enumerate(data_x):
        bow = []
        text = lemmatizer.lemmatize(doc.lower())
        for word in words:
            bow.append(1) if word in text else bow.append(0)

        # mark the index of classes that the current pattern is associated to
        output_row = list(output_empty)
        output_row[classes.index(data_y[idx])] = 1

        training.append([bow, output_row])

    # shuffle the data and convert it to an array
    random.shuffle(training)
    training = np.array(training, dtype=object)
    # split the features and target labels
    train_X = np.array(list(training[:, 0]))
    train_Y = np.array(list(training[:, 1]))
    print("Training data created")

    # Build Neural network
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_X[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_Y[0]), activation='softmax'))

    adam = tf.keras.optimizers.Adam(learning_rate=0.01, weight_decay=1e-6)
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

    # fitting and saving the model
    hist = model.fit(np.array(train_X), np.array(train_Y), epochs=200, batch_size=5, verbose=1)
    model.save('chatbot_model.h5', hist)

    print("-----model created-------")
    # print(model.summary())
