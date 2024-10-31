import subprocess


class Learner:
    def __init__(self):
        self.alphabet = ["S", "N", "W", "E"]
        self.S = [""]
        self.E = [""]
        self.extraS = []
        self.extra_table = {}
        self.mat = subprocess.Popen(
            ["python3", "MAT/tfl-lab2/main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        self.table = {("", ""): self.get_membership("")}
        self.add_extraS("")

    def get_membership(self, word):
        self.mat.stdin.write("isin\n")
        self.mat.stdin.write(f"{word}\n")
        self.mat.stdin.flush()

        result = self.mat.stdout.readline().strip()
        return result == "True"

    def get_equal(self):
        self.mat.stdin.write("equal\n")
        columns = ""
        for suf in self.E:
            if suf == "":
                columns += "e"
            else:
                columns += suf
            columns += " "
        self.mat.stdin.write(f"{columns.strip()}\n")

        for s in self.S:
            row = ""
            if s == "":
                row += "e" + " "
            else:
                row += s + " "
            for suf in self.E:
                row += str(int(self.table[(s, suf)])) + " "
            self.mat.stdin.write(f"{row.strip()}\n")
        self.mat.stdin.write("end\n")
        self.mat.stdin.flush()

        res = self.mat.stdout.readline().strip()
        if res == "TRUE":
            return True, None
        return False, res

    def add_extraS(self, new_prefix):
        for a in self.alphabet:
            if (new_prefix + a) not in self.extraS:
                self.add_row(new_prefix + a, True)

    def add_row(self, prefix, extra):
        if extra:
            self.extraS.append(prefix)
            for e in self.E:
                if (prefix, e) not in self.extra_table:
                    self.extra_table[(prefix, e)] = self.get_membership(prefix + e)
        else:
            self.S.append(prefix)
            for e in self.E:
                if (prefix, e) not in self.table:
                    self.table[(prefix, e)] = self.get_membership(prefix + e)

    # проверка на полноту и исправление
    def full_table(self):
        full = False
        while not full:
            full = True
            for es in self.extraS:
                involve = False
                for s in self.S:
                    same = True
                    for e in self.E:
                        if not self.extra_table[(es, e)] == self.table[(s, e)]:
                            same = False
                            break
                    if same:
                        involve = True
                        break
                if not involve:
                    full = False
                    self.S.append(es)
                    self.extraS.remove(es)
                    for e in self.E:
                        self.table[(es, e)] = self.extra_table[(es, e)]
                        del self.extra_table[(es, e)]
                    self.add_extraS(es)

    def add_suffix(self, new_suffix):
        self.E.append(new_suffix)
        for s in self.S:
            self.table[(s, new_suffix)] = self.get_membership(s + new_suffix)
        for es in self.extraS:
            self.extra_table[(es, new_suffix)] = self.get_membership(es + new_suffix)

    def format_table(self):
        """преобразует переменную table в читаемый формат для вывода"""
        # заменяем пустые строки на e для представления префиксов и суффиксов
        suff_row = ["e" if e == "" else e for e in self.E]

        # заголовок строки с суффиксами
        readable_table = "\t" + "\t".join(suff_row) + "\n"

        # генерация строк для каждого префикса с соответствующими значениями
        for s in self.S:
            row = []
            for e in self.E:
                value = self.table.get((s, e), 0)  # получаем значение для комбинации (s, e), если отсутствует — 0
                row.append(str(int(value)))
            s_label = "e" if s == "" else s  # Обозначаем пустой префикс как e
            readable_table += f"{s_label:<4}\t" + "\t".join(row) + "\n"
        print(readable_table)

    def log_table(self):
        output = open('log.txt', 'w')
        print("equal", file=output)
        columns = ""
        for suf in self.E:
            if suf == "":
                columns += "e"
            else:
                columns += suf
            columns += " "
        print(f"{columns.strip()}", file=output)

        for s in self.S:
            row = ""
            if s == "":
                row += "e" + " "
            else:
                row += s + " "
            for suf in self.E:
                row += str(int(self.table[(s, suf)])) + " "
            print(f"{row.strip()}", file=output)
        print("end", file=output)

    def run(self):
        while True:
            self.full_table()
            
            equal, contr = self.get_equal()

            if equal:
                print("Автомат построен.")
                self.format_table()
                self.log_table()
                break
            else:
                print("Получен контрпример: ", contr)
                # обновляем списки суффиксов уникальными значениями из контрпримера
                for i in range(len(contr)):
                    suf = contr[i:]
                    if suf not in self.E:
                        self.add_suffix(suf)

    def close(self):
        self.mat.terminate()


def main():
    learner = Learner()
    learner.run()
    learner.close()


if __name__ == "__main__":
    main()
