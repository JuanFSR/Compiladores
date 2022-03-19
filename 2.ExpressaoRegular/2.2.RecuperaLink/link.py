import re

def main():
    with open('pagina-html.html', 'r', encoding='utf-8') as h:
        # [^href=]*"(.*?)"
        listLink = []
        for line in h:
            link = re.findall(r'(?<=href=")(https:\/\/)(.)+(?=")', line)
            if len(link) > 0 :
                listLink.append(link[0])

    with open('links.txt', 'w') as l:
        [l.write(i + "\n") for i in listLink]

if __name__ == "__main__":
    main()