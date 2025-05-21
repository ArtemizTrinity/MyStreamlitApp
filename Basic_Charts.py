import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

col_names = ['A', 'B', 'C']

data = pd.DataFrame(np.random.randint(30, size=(30,3)), columns=col_names)

'line graph:'
st.line_chart(data)
