import yaml
import argparse

########################################################################################################################

def table_generator():
    """
    Creates two nested dictionaries for both encoding and decoding a vingere cipher. Decoding the cipher could be
    achieved with a reverse lookup of the `encrypt` dictionary but creating the 'decrypt' dictionary now is cheap and
    saves multiple conditional evaluations later on and facilitates re-using the converter function interchangebly later

    :return: (encrypt, decrypt): (dict, dict) 2d grid of shifted alphabets for columns, standard for vigene ciphers

    """
    encrypt = {}
    decrypt = {}

    alphabet = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'  # the alphabet twice to allow looping through
    alpha_len = 26

    for i, j in enumerate(alphabet[:alpha_len]):  # iterate various alphabets (a-z, b-a, c-b ... z-a)
        letter = alphabet[i:alpha_len+i]
        encrypt[letter[0]] = {a:l for a,l in zip(alphabet, letter)}
        decrypt[letter[0]] = {l:a for l,a in zip(letter, alphabet)}

    return encrypt, decrypt


########################################################################################################################


def message_matcher(message, key_phrase):
    """
    Produces a  key stream from the passed message and key phrase which is the number of repetitions needed for the
    original keyphrase to match the length of the message. Where this is a non integer value, the key phrase is sliced
    using the modulus of the two inputs. Can be used for both decryption and encryption.

    :param message: str, the message to be converted by the program
    :param key_phrase: str, the user key phrase used to facilitate the vigene cipher

    :return: matched_len: str, repeated key phrase matching the length of the original message

    """
    message_len, kp_len = len(message), len(key_phrase)

    num_reps = int(message_len / kp_len)
    excess = message_len % kp_len
    matched_len = (key_phrase * num_reps) + key_phrase[:excess]

    assert len(matched_len) == message_len, "Length of user message and generated key phrase do not match"

    return matched_len


########################################################################################################################


def converter(key_stream, message, tabula_recta):
    """
    Either encrypts or decrypts a passed message accordging to the key_stream depending on the tabula_recta passed
    in line with a vigene cipher (2D table look up of alpha indexed along both axis).
    Only alpha characters exist within the table so only they are converted here. A comprehension could likely be used
    but this keeps it a bt more readable, stops me having to use a join method and allows me to revisit what to do with
    non alpha characters in future.

    :param key_stream: str, matched length user key phrase, repeated until matches length of user message
    :param message: str, to be converted depending on the arrangement of the passed 2D table
    :param tabula_recta: dict, nested dictionary of alpha keys which is parsed to convert the passed message

    :return: converted: str, message which has undergone transformation through the cipher 2D lookup

    """
    converted = ''
    for k, m in zip(key_stream, message):  # cant convert punctuation and numbers so conditional checks against that
        if m.isalpha():
            converted += tabula_recta[k][m]  # 2D nested dictionary lookup [letter][letter]
        else:
            converted += m

    return converted


########################################################################################################################


def encryptor(key_phrase, encrypt_table, filename, user_break):
    """
    Continually accepts user input from the command line until the break condtion is specified by the user. Unless the
    input is the break, each line inputted is encrypted and appended to a text file with a newline character.

    :param key_phrase: str, user key to encrypt the message against
    :param encrypt_table: dict, 2D nested dictionary which user message is passed to for encryption
    :param filename: str, path to file that the user entry is to be written to
    :param user_break: str, code specified by the user to stop writing lines to the encrypted file

    :return: None

    """
    with open(filename, 'a')as f:
        while True:
            message = input(F' {user_break} ').lower()
            if message == user_break:
                break
            key_stream = message_matcher(message, key_phrase)
            encrypted = converter(key_stream, message, encrypt_table)
            f.write(encrypted+'\n')


########################################################################################################################


def decryptor(key_phrase, decrypt_table, filename):
    """
    Reads a pre-existing user encrypted file, decrypts the file and then prints the decrypted file to the terminal.
    Note, the correct key phrase used to originally encrypt the contents must be used to decrypt it otherwise will just
    get a garbled mess out.

    :param key_phrase: str, user key to decrypt the message against
    :param decrypt_table: dict, 2D nested dictionary which user message is passed to for decryption
    :param filename: str, path to file that is to be read from and decrypted

    :return: None

    """
    with open(filename, 'r') as f:
        for line in f.readlines():
            key_stream = message_matcher(line, key_phrase)
            entry = converter(key_stream, line, decrypt_table).strip('\n')
            print(entry)


########################################################################################################################


def main(args, config):
    """
    Given a user key and the function to either encrypt a passed message or decrypt stored messages, perform said action
    The file the encrypted text is written to / decrypted text is read from is a default however can be changed
    by the user by passing the `-f`

    :param args: argparse.Namespace, all command line arguments passed by user are contained here
    :param config: dict, user saved settings loaded from the config file

    :return: None

    """
    key_phrase, filename = args.key.lower(), args.file  # user key to encrypt/decrypt
    assert key_phrase.isalpha(), 'Key word must not contain non alphabet characters'

    encrypt_table, decrypt_table = table_generator()

    if args.encrypt:  # perform user specified function or print an error if no valid choice is passed
        encryptor(key_phrase, encrypt_table, filename, config['Terminator'])
    elif args.decrypt:
        decryptor(key_phrase, decrypt_table, filename)
    else:
        print('Please specify `-e` to encrypt or `-d` to decrypt')

########################################################################################################################

if __name__ == '__main__':

    with open('config.yml', 'r')as f:  # retrieve user specific configurations for filename and terminator key
        config = yaml.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', help='User key to encrypt and decrypt message')
    parser.add_argument('-f', '--file', action='store', default=config['File'], help='non default file path if desired')
    parser.add_argument('-e', '--encrypt', action='store_true', help='Include flag to write encrypted message to file')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Include flag to read encrypted message from file')
    args = parser.parse_args()

    main(args, config)  # pass all setting and begin script
