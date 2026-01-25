from pipeline.controller import Pipeline
from programs import sum

print("="*50)
print("test 1: simple add")
print("="*50)

instructions = sum.get_program()
pipeline = Pipeline(instructions)
pipeline.run()

print(f"\nvreau: x3=8")
print(f"am: x3={pipeline.registers.read(3)}")
print(f"status: {'OK' if pipeline.registers.read(3) == 8 else 'FAIL'}")

with open("test_rez.txt", "w") as g:
    g.write(f"{pipeline.registers}\n")
    g.write(f"{pipeline.cycle-1} cicluri de ceas \n")
    if pipeline.registers.read(3) ==8:
        g.write(f"x3 este 8, cum trebuie")
    else:
        g.write(f"x3 este gresit, {pipeline.registers.read(3)}")

