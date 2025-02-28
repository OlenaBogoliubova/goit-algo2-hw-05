import time
import re
import mmh3
import math

class HyperLogLog:
    def __init__(self, p=5):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._get_alpha()
        self.small_range_correction = 5 * self.m / 2  # Поріг для малих значень

    def _get_alpha(self):
        if self.p <= 16:
            return 0.673
        elif self.p == 32:
            return 0.697
        else:
            return 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        x = mmh3.hash(str(item), signed=False)
        j = x & (self.m - 1)
        w = x >> self.p
        self.registers[j] = max(self.registers[j], self._rho(w))

    def _rho(self, w):
        return len(bin(w)) - 2 if w > 0 else 32

    def count(self):
        Z = sum(2.0 ** -r for r in self.registers)
        E = self.alpha * self.m * self.m / Z
        
        if E <= self.small_range_correction:
            V = self.registers.count(0)
            if V > 0:
                return self.m * math.log(self.m / V)
        
        return E

def load_ip_addresses(filename):
    """ Завантаження IP-адрес із лог-файлу, ігноруючи некоректні рядки """
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ip_addresses = []
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            match = ip_pattern.search(line)
            if match:
                ip_addresses.append(match.group())
    
    return ip_addresses

def count_unique_ips_exact(ip_addresses):
    """ Точний підрахунок унікальних IP-адрес за допомогою set """
    return len(set(ip_addresses))

def count_unique_ips_hyperloglog(ip_addresses, p=14):
    """ Наближений підрахунок унікальних IP-адрес за допомогою HyperLogLog """
    hll = HyperLogLog(p)
    for ip in ip_addresses:
        hll.add(ip)
    return hll.count()

if __name__ == "__main__":
    filename = "C:/Users/Elena/Desktop/MasterIT/Tier 1 Math/Algorithm/Algo2/lms-stage-access.log" 
    ip_addresses = load_ip_addresses(filename)
    
    # Точний підрахунок
    start_time = time.time()
    exact_count = count_unique_ips_exact(ip_addresses)
    exact_time = time.time() - start_time
    
    # HyperLogLog підрахунок
    start_time = time.time()
    hll_count = count_unique_ips_hyperloglog(ip_addresses)
    hll_time = time.time() - start_time
    
    # Вивід результатів у вигляді таблиці
    print("Результати порівняння:")
    print(f"{'Метод':<25}{'Точний підрахунок':<20}{'HyperLogLog':<20}")
    print(f"{'Унікальні елементи':<25}{exact_count:<20}{hll_count:<20}")
    print(f"{'Час виконання (сек.)':<25}{exact_time:<20.6f}{hll_time:<20.6f}")
