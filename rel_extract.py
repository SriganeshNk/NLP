import re


def find_college(college, line):
    i = 0
    institution = []
    for x in range(len(line)):
        if line[x].strip('.') == college:
            i = x
            school = line[x]
            while i - 1 > -1:
                if line[i - 1].istitle():
                    school = line[i - 1] + ' ' + school
                    i -= 1
                else:
                    break
            i = x
            while i + 1 < len(line):
                if line[i + 1].istitle():
                    school += ' ' + line[i + 1]
                    i += 1
                else:
                    break
            institution.append(school)
    print institution
    return institution


def extract():
    f = open('train.tsv', 'r')
    person, institution, sentences, labels = [], [], [], []
    for line in f:
        line = line.split('\t')
        person.append(line[0].strip())
        institution.append(line[1].strip())
        sentences.append(line[2].strip())
        labels.append(line[3].strip())
    pattern = ['College', 'School', 'University']
    for line in sentences:
        for x in pattern:
            match = re.finditer(x, line, flags=re.IGNORECASE)
            if match is not None:
                for m in match:
                    college = line[m.start():m.end()]
                    print college
                    find_college(college, line.split())
        print line
    """print sentences[34]
    print sentences[20]"""


if __name__ == "__main__":
    extract()