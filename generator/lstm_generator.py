'''
Created on 11 august 2018
@author: juliette.bourquin
'''
import os
import random
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.utils import np_utils

class lstm_generator:
    
    def __init__(self, master):
        
        self.master = master
        self.text = self.assemble_corpus(master)
        self.starts = [h for h in self.text.split('\n') if len(h) > 1]
        self.characters = sorted(list(set(self.text)))
        self.n_to_char = {n:char for n, char in enumerate(self.characters)}
        self.char_to_n = {char:n for n, char in enumerate(self.characters)}
        

    # future function used to unite all authors from a dir into one piece
    def assemble_corpus(self, directory):
        global_content = ''
        for file in os.listdir(directory):
            if file.endswith('.txt'):
                with open(directory+'/'+file, 'r', encoding='utf-8') as rf:
                    global_content += rf.read()
        #return global_content
        return '\n'.join(global_content.split('\n')[0:5000])
    
    def train_model(self, text, neurons, epochs, poem_size):
         
        X = []
        Y = []
        length = len(text)
        seq_length = 2
        for i in range(0, length-seq_length, 1):
            sequence = text[i:i + seq_length]
            label =text[i + seq_length]
            X.append([self.char_to_n[char] for char in sequence])
            Y.append(self.char_to_n[label])
            
        X_modified = np.reshape(X, (len(X), seq_length, 1))
        X_modified = X_modified / float(len(self.characters))
        Y_modified = np_utils.to_categorical(Y)
        
        model = Sequential()
        model.add(LSTM(neurons, input_shape=(X_modified.shape[1], X_modified.shape[2]), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(neurons, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(neurons))
        model.add(Dropout(0.2))
        model.add(Dense(Y_modified.shape[1], activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        
        model.fit(X_modified, Y_modified, epochs=epochs, batch_size=50)
        
        model_name = 'haikus_' + str(neurons) + '_' + str(epochs) + '.h5' 
        
        model.save_weights(model_name)
        model.load_weights(model_name)
        inspiration = random.choice(self.starts)
        
        string_mapped = []
        for i in range(0, seq_length):
            string_mapped.append(self.char_to_n[inspiration[i]])#X[seq_length-1]
        full_string = [self.n_to_char[value] for value in string_mapped]
        
        # generating characters
        for i in range(poem_size):
            x = np.reshape(string_mapped,(1,len(string_mapped), 1))
            x = x / float(len(self.characters))
        
            pred_index = np.argmax(model.predict(x, verbose=0))
            #seq = [n_to_char[value] for value in string_mapped]
            full_string.append(self.n_to_char[pred_index])
        
            string_mapped.append(pred_index)
            string_mapped = string_mapped[1:len(string_mapped)]
    
        #combining text
        txt=""
        for char in full_string:
            txt = txt+char
        return txt
    
    def add_to_manuscript(self, filename, haiku):
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write('\n\n' + haiku)

if __name__ == '__main__' :
    
    manuscript = 'written_haikus.txt'
    master = '../sourcetexts'
    generator = lstm_generator(master)
    poem = generator.train_model(generator.text, 5, 10, 20)
    print(poem)
    generator.add_to_manuscript(manuscript, poem)
