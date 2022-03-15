import re

def main():
    with open('pagina-html.html', 'r') as h:
        
        for line in h:
            links = re.findall(r'(?<=href=")https:.*?(?=")', line)

    with open('links.txt', 'w') as l:
        [l.write(i + "\n") for i in links]

if __name__ == "__main__":
    main()