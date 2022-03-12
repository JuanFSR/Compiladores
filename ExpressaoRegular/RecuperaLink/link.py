import re

def main():
    with open('pagina-html.html', 'r') as h:
        line = h.readlines()
        
        for i in line:
            links = re.findall(r"<href", i)
            print(links)



if "__name__" == "__main__":
    main()