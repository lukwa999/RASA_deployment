import matplotlib.pyplot as plt
import pandas as pd

# Sample data
data = {
    'Intents': ['everyday_open_everyday_close', 'ask_time_open_close', 'ask_day_open_close', 'tutor_step', 'tutor_available','renew_book',
                'ask_proxy', 'proxy_step'],
    'Bounding boxes': [30, 45,50,36,30,46,33,33]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(10, 6))
bars = plt.barh(df['Intents'], df['Bounding boxes'], color='lightblue')

# Adding the values on the bars
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
             f'{bar.get_width()}', va='center', ha='left', color='black')

plt.xlabel('Bounding boxes')
plt.ylabel('Intents')
plt.title('Scope Questions')
plt.show()
