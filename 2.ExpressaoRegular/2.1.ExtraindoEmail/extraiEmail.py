import re

# Regex: \w+[\+\|.|\w]*@[.|\w]+
def main():
    with open('e-mails.txt', 'r') as e:
        line = e.readlines()
        listEmail = []


        # Não pode começar com número
        for pos in line:
            email = re.findall(r"(?<=\<)[a-z][\w|\.]*@([a-z]+\.[a-z]+)(\.[a-z]+)*(?=\>)", pos)
            listEmail.append(email[0]+ "\n")


    with open('saida-email.txt', "w") as s:
        [s.writelines(i) for i in listEmail]
    
if __name__ == "__main__":
    main()

