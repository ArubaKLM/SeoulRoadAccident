import matplotlib as mpl
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import pandas as pd
import openpyxl as op
import matplotlib.font_manager as fm

# 설치된 폰트 출력
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'NanumGothic'

# 세팅 불러오기
st.set_page_config(
    page_title="서울시 교통사고 현황",
    page_icon="Cars",
    #layout="wide",
)

st.markdown('<style>div.appview-container{background-color: #f7f6f4;}</style>',unsafe_allow_html=True)
st.markdown('<style>div[data-testid="stForm"]{background-color: #fcfbfb;}</style>',unsafe_allow_html=True)
st.markdown('<style>section[data-testid="stSidebar"]{background-color: #dfdedd;}</style>',unsafe_allow_html=True)

st.title("서울시 교통사고 현황")


# ========== data & setup
@st.cache
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/ArubaKLM/Viz-Practice/main/road_accident_data.csv")
    return df

df = load_data() 

# ========== SIDEBAR
# Customise map
st.sidebar.subheader("디자인 조정")

with st.form(key = 'Form1'):
    with st.sidebar:
        main_title = st.text_input("제목", "서울시 교통사고 현황")
        title_fontsize = st.number_input("제목 크기", min_value=10, max_value=40, value=30)
        clr_title = st.color_picker('제목 색상', '#184e77')
        clr_background = st.color_picker('배경 색상', '#f7f6f4')
        clr_value = st.color_picker('수치 색상', '#1D4D79')
        clr_line = st.color_picker('선 색상', '#EC0808')
        clr_area = st.color_picker('영역 색상', '#F16322')
        alpha_area = st.number_input("투명도: 0(투명) ~ 1(불투명)",min_value=0.00, max_value=1.00, value=0.5)
        submitted = st.form_submit_button('적용하기')

# =========== FILTER SELECTIONS

row_0, row_01 = st.columns([1,2])

with st.form(key='columns_in_form'):
    st.markdown('데이터 탐색하기')
    col1, col2 = st.columns(2)
    with col1:
        Harm = st.radio("harm",('totalcase', 'injured', 'death'))
    with col2:
        Category = st.radio("category", ('total', 'CtoP', 'CtoC', 'CarOnly'))
    submitted = st.form_submit_button('적용하기')
    # 기간 추가해서 조정할 수 있도록 해보자

footer = "원데이터: https://data.seoul.go.kr/dataList/322/S/2/datasetView.do \n 제작: 윤준식 | Lisa Hornung의 https://github.com/liloho/london-cycling-rates 프로젝트를 참고하여 제작함"
subtitle = "2007~2021년 서울시 자치구별" + Harm.lower() + Category.lower() # ex 차대차 사망건수

st.write("")

# Dictionaries
display_dict = {'jong':'종로', 'jungg':'중구', 'yong':'용산', 
                'sungd':'성동', 'gwang':'광진', 'dongd':'동대문', 'jungr':'중랑', 
                'sungb':'성북', 'gangb':'강북', 'dob':'도봉', 'now':'노원', 
                'eun':'은평', 'seod':'서대문', 'ma':'마포', 
                'yang':'양천', 'gangs':'강서', 'gur':'구로', 'gum':'금천', 
                'yeong':'영등포', 'dongj':'동작', 'gwan':'관악', 
                'seo':'서초', 'gangn':'강남', 'song':'송파', 'gangd':'강동'}

# =========== VISUALISATION

# Map view

## Plotting
#filter data set based on input

data = df[(df["district"].isin(display_dict.keys())) & (df["harm"]==Harm) & (df["category"]==Category)].reset_index()
data["Display Name"] = data["district"].map(display_dict)

# ========= Layout
# Initialise Figure and define layout
#8,7 | 10, 8.75
layout = [
        ["___","___","___","___","도봉","___","___","___"],
        ["___","___","은평","___","강북","노원","___","___"],
        ["___","___","서대문","종로","성북","동대문","중랑","___"],
        ["___","___","마포","중구","성동","광진","___","___"],
        ["___","___","___","용산","___","___","___","___"],
        ["강서","양천","영등포","___","서초","강남","송파","강동"],
        ["___","구로","금천","동작","___","___","___","___"],
        ["___","___","___","관악","___","___","___","___"],
        ]
fig,axs = plt.subplot_mosaic(layout, figsize=(16,12), empty_sentinel="___") 

fig.set_facecolor(clr_background)
plt.subplots_adjust(wspace=0.1, hspace=0.1, left=0.05, right=0.95, bottom=0.05, top=0.9)

#=========== Plotting
# 자치구 표시하기
y_values = ['2007', '2008', '2009', '2010' ,'2011',
            '2012', '2013', '2014', '2015', '2016',
            '2017', '2018', '2019', '2020', '2021']        
x_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
height = max(data[y_values].max()) + 50

## Loop through all boroughs and map their values
for ax in axs:
    data_filtered = data[data["Display Name"]==ax]
        
    #구의 이름 나타내기
    axs[ax].text(1.05, height, ax, fontsize=15, ha="left", va='top', color="#111111")
    
    #영역 나타내기
    axs[ax].fill_between(x_values, list(data_filtered[y_values].values[0]), 
                         zorder=1, color=clr_area, alpha=0.7, linewidth=0)   
    axs[ax].plot(x_values, list(data_filtered[y_values].values[0]), zorder=2, 
             color=clr_line,linewidth=2.5)    
    
    #마지막 연도 점 나타내기
    axs[ax].scatter(max(x_values), list(data_filtered[y_values].values[0])[-1], zorder=3,color=clr_line)
    
    #최신 연도의 수치 나타내기
    axs[ax].text(max(x_values)+2, height, 
                 '{:<10d}'.format(list(data_filtered[y_values].values[0])[-1]), 
                 ha="right", va='top',
                 fontsize=20, fontweight='bold', color=clr_value)
    
    #영역 색 설정
    axs[ax].set_xlim(xmin=0.9, xmax=15.1)
    axs[ax].set_ylim(ymax=height, ymin=0) 
    axs[ax].set_facecolor(clr_background)    
    axs[ax].axis("off")

#============= 범례           
#add legend
lgd = fig.add_axes([0.8, 0.05, 0.1, 0.1]) #axes to hold legend
lgd.text(1.05,height-3,data["district"][0], fontsize=8, ha="left", va='top', color="#111111")
lgd.fill_between(x_values,list(data.loc[0][y_values].values), zorder=1,color="#999999", alpha=0.7,linewidth=0)    
lgd.plot(x_values,list(data.loc[0][y_values].values), zorder=2,color="#333333",linewidth=1.5)    
lgd.scatter(max(x_values),list(data.loc[0][y_values].values)[-1], zorder=3,color="#333333")
lgd.text(max(x_values)-0.2, height-2, '{:<10d}'.format(list(data.loc[0][y_values].values)[-1]), 
        ha="right", fontsize=15, fontweight='bold', va='top', color="#333333")
lgd.set_xlim(xmin=0.8, xmax=15.2)
lgd.set_ylim(ymax=height, ymin=0) 
lgd.set_facecolor("#E4E4E4")
for pos in ["top", "bottom", "right", "left"]:
    lgd.spines[pos].set_visible(False)
lgd.set_xticks([1,15], ["2007", "2021"],fontsize = 10)
lgd.set_yticks([])
lgd.annotate('2021년의\n수치', xy=(max(x_values)+0.3, height-10), xycoords='data', xytext=(5, 0), textcoords='offset points', 
                   fontsize=15, ha='left', va='center', annotation_clip=False,
                    arrowprops=dict(arrowstyle="->",facecolor='black'))
lgd.annotate('자치구', xy=(min(x_values)+0.2, height-1), xycoords='data', xytext=(0, 16), textcoords='offset points', 
                   fontsize=15, ha='center', va='center', annotation_clip=False,
                    arrowprops=dict(arrowstyle="->",facecolor='black'))



#=============== Text           
## Add titles and footer
y_pos = 1.05
x_pos = 0.05

fig.text(x_pos, y_pos, main_title, fontsize=title_fontsize, ha='left',va="top",
             fontweight="bold",  color=clr_title)
fig.text(x_pos, y_pos-(title_fontsize*0.2*0.01), subtitle, fontsize=15, ha='left',va="top",
             fontweight="normal",   color="#111111")
fig.text(x_pos, -0.05, footer, fontsize=11, ha='left',va="center",
             fontweight="normal",  linespacing=1.5, color="#111111")


#============ 서울시 전체
#inner = df[(df["Area name"]=="Inner London") & (df["Frequency"]==frequency) & (df["Purpose"]==purpose)]["2021"].iloc[0]
#outer = df[(df["Area name"]=="Outer London") & (df["Frequency"]==frequency) & (df["Purpose"]==purpose)]["2021"].iloc[0]
#강동
#강북
#서북
#도심
Seoul = df[(df["district"]=="seoul") & (df["category"]==Category) & (df["harm"]==Harm)]["2021"].iloc[0]

fig.text(x_pos, y_pos-0.14,  "2021년 전체: " + ''.format(Seoul), fontsize=15, ha='left',va="top",
         fontweight="bold",color=clr_value)

st.pyplot(fig)


## ======= Download
st.write("")
st.write("")

# download data
csv = data[['district', 'category','harm','2016', '2017', '2018','2019', '2020','2021']].to_csv(index=False)
#목록 열거

st.download_button(
    label="CSV로 데이터 내려받기",
    data=csv,
    file_name='seoul_car_accident_%s_%s.csv' % (Harm.lower(), Category.lower()),
    mime='text/csv',
)

#download image
plt.savefig("seoul_car_accident.png",bbox_inches="tight", pad_inches=0.2)
with open("seoul_car_accident.png", "rb") as file:
    btn = st.download_button(
            label="이미지 저장하기",
            data=file,
            file_name="seoul_car_accident",
            mime="image/png"
          )

st.write("")
st.subheader("About")
st.markdown("Data source: [Active Lives Survey 2021](https://www.gov.uk/government/statistics/walking-and-cycling-statistics-england-2021)")
st.markdown("App created by Lisa Hornung. Visit my [website](https://inside-numbers.com/) or follow me on [Github](https://github.com/Lisa-Ho), [Mastodon](https://fosstodon.org/@LisaHornung), [Twitter](https://twitter.com/LisaHornung_).")