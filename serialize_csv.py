import pickle

def csv_to_byte(path):
    with open(path) as f:
        data = [line.split(',') for line in f.readlines()]

    serialized_data = pickle.dumps(data)
    return serialized_data

if __name__ == '__main__':
    print(csv_to_byte('data.csv'))
