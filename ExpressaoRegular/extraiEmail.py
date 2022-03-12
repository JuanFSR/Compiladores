import re

# ([aA-zZ]+|[0-9]+|^<).([aA-zZ]+|[0-9]+|.)@[^>,]+
def main():
    with open('e-mails.txt', 'r') as e:
        # data = e.readlines()
        for line in e:
            print(line)

if __name__ == "__main__":
    main()

