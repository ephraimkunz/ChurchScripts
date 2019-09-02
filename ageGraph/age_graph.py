from lcr import API as LCR
import matplotlib.pyplot as plt
from statistics import mean, median, mode
import os


with open('cred') as f:
    for line in f:
        line = line.strip('\n')
        pieces = line.split('=')
        if len(pieces) == 2:
            os.environ[pieces[0]] = pieces[1]

user = os.environ['LDS_USER']
password = os.environ['LDS_PASSWORD']
unit_number = os.environ['LDS_UNIT_NUMBER']

lcr = LCR(user, password, unit_number)

member_list = lcr.members_alt()
member_list = [member for member in member_list if member['age'] <= 29]
member_dict = {}
for member in member_list:
    age = member['age']
    member_dict[age] = member_dict.get(age, 0) + 1

x_data = sorted(list(member_dict.keys()))
y_data = [member_dict[age] for age in x_data]

all_ages = []
for age in x_data:
    all_ages += [age] * member_dict[age]

print("\nAll members ({}):\nMean: {}\nMedian: {}\nMode: {}\n".format(len(all_ages), mean(all_ages), median(all_ages), mode(all_ages)))

maxY = member_dict[max(member_dict, key=member_dict.get)]

plt.style.use('ggplot')
plt.suptitle('Standford YSA Ward age distribution')

# PLot 1
plt.subplot(1, 3, 1)
x_pos = [i for i, _ in enumerate(x_data)]

plt.bar(x_pos, y_data, color='green')
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("All")

axes = plt.gca()
axes.set_ylim([0, maxY])

plt.xticks(x_pos, x_data)

# Plot 2
plt.subplot(1, 3, 2)
member_dict.clear()
for member in member_list:
    if member['sex'] == 'M':
        age = member['age']
        member_dict[age] = member_dict.get(age, 0) + 1

x_data = sorted(list(member_dict.keys()))
y_data = [member_dict[age] for age in x_data]

all_ages = []
for age in x_data:
    all_ages += [age] * member_dict[age]

print("Male members ({}):\nMean: {}\nMedian: {}\nMode: {}\n".format(len(all_ages), mean(all_ages), median(all_ages), mode(all_ages)))

x_pos = [i for i, _ in enumerate(x_data)]

plt.bar(x_pos, y_data, color='green')
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("Male")

axes = plt.gca()
axes.set_ylim([0, maxY])

plt.xticks(x_pos, x_data)

# Plot 3
plt.subplot(1, 3, 3)

member_dict.clear()
for member in member_list:
    if member['sex'] != 'M':
        age = member['age']
        member_dict[age] = member_dict.get(age, 0) + 1

x_data = sorted(list(member_dict.keys()))
y_data = [member_dict[age] for age in x_data]

all_ages = []
for age in x_data:
    all_ages += [age] * member_dict[age]

print("Female members ({}):\nMean: {}\nMedian: {}\nMode: {}\n".format(len(all_ages), mean(all_ages), median(all_ages), mode(all_ages)))

x_pos = [i for i, _ in enumerate(x_data)]

plt.bar(x_pos, y_data, color='green')
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("Female")

axes = plt.gca()
axes.set_ylim([0, maxY])

plt.xticks(x_pos, x_data)

plt.show()
