#import matplotlib.pyplot
import matplotlib.pyplot as plt

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
valores = [105235, 107697, 110256, 109236, 108859, 109986]

matplotlib.pyplot.plot(meses, valores)
matplotlib.pyplot.title('Faturamento no primeiro semestre de 2017')
matplotlib.pyplot.ylabel('Faturamento em R$')
matplotlib.pyplot.show()