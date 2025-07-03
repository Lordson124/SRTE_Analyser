import pandas as pd
import numpy as np
import re

def get_comments(df, columns):
    # to_remove = ['Nil','None','NIL','null','Null','Nothing','nill',
    #     'nil','nothing','non','Nill','NILL','N/A','N/C','nothing else',
    #     'NOTHING ELSE', 'Nun', u'\u2019', 'none'
    # ]
    if len(columns) <= 5:
        comments = []
        for col in columns:
            df[col] = df[col].apply(lambda x: re.sub(r'\-|\d.\s|[.?_!*]+', '', str(x)))
            # for w in to_remove:
            comment = (df[col].str.replace('Nan', '').replace('Nil', '')
                    .replace('None', '')
                    .replace('NIL', '')
                    .replace('null', '')
                    .replace('Null', '')
                    .replace('Nothing', '')
                    .replace('nill','')
                    .replace('nil','')
                    .replace('nothing','')
                    .replace('non','')
                    .replace('Nill', '')
                    .replace('NILL', '')
                    .replace('N/A', '')
                    .replace('N/C', '')
                    .replace('nothing else', '')
                    .replace('nun','')
                    .replace('NOTHING ELSE', '')
            )
            comments.append(comment)
    else:
        comments = []
        df[columns] = df[columns].apply(lambda x: re.sub(r'\-|\d.\s|[.?_!*]+', '', str(x)))
        # for w in to_remove:
        comment = (df[columns].str.replace('\n', ', ').replace('\r', '')
                .replace('Nan', '').replace('Nil', '')
                .replace('None', '')
                .replace('NIL', '')
                .replace('null', '')
                .replace('Null', '')
                .replace('Nothing', '')
                .replace('nill','')
                .replace('nil','')
                .replace('nothing','')
                .replace('non','')
                .replace('Nill', '')
                .replace('NILL', '')
                .replace('N/A', '')
                .replace('N/C', '')
                .replace('nothing else', '')
                .replace('nun','')
                .replace('NOTHING ELSE', '')
        )
        comments.append(comment)
    return comments

def get_series(df):
    # to_remove = ['Nil','None','NIL','null','Null','Nothing','nill',
    #     'nil','nothing','non','Nill','NILL','N/A','N/C','nothing else',
    #     'NOTHING ELSE', 'Nun', u'\u2019', 'none'
    # ]
    comments = []
    df = df.apply(lambda x: re.sub(r'\-|\d.\s|[.?_!*]+', '', str(x)))
    # for w in to_remove:
    comment = (df.str.replace('Nan', '').replace('Nil', '')
                .replace('None', '')
                .replace('NIL', '')
                .replace('null', '')
                .replace('Null', '')
                .replace('Nothing', '')
                .replace('nill','')
                .replace('nil','')
                .replace('nothing','')
                .replace('non','')
                .replace('Nill', '')
                .replace('NILL', '')
                .replace('N/A', '')
                .replace('N/C', '')
                .replace('nothing else', '')
                .replace('nun','')
                .replace('NOTHING ELSE', '')
    )
    comments.append(comment)
    return comments


def cleanup(x):
    g = []
    for i in x:
        for r in i:
            if r != '':
                g.append(r)
    return list(dict.fromkeys(np.sort(g)))

def cleanitup(x):
    g = []
    for i in x:
        for r in i:
            if r != '':
                g.append((str((r.encode("ascii", "ignore")).decode()).capitalize()).strip())
    return list(dict.fromkeys(np.sort(g)))

def extract_series(df, name):
    # likes = df.columns[2:5]
    # dislikes = df.columns[5:9]

    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_series(df)), fmt='%s', delimiter='\n')
    # np.savetxt('C:/Users/OIE Unit/Desktop/Comments extraction/Dislikes about the course.txt',
    #            cleanup(get_comments(filter_course, dislikes)), fmt='%s', delimiter='\n')

    print('Comments successfully extracted...')
  
     
def extract_df(df, name, col):
    # likes = df.columns[2:5]
    # dislikes = df.columns[5:9]

    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_comments(df, col)), fmt='%s', delimiter='\n')
    # np.savetxt('C:/Users/OIE Unit/Desktop/Comments extraction/Dislikes about the course.txt',
    #            cleanup(get_comments(filter_course, dislikes)), fmt='%s', delimiter='\n')

    print('Comments successfully extracted...')

# def extract_likes(df, filter_course):
#     likes = df.columns[2]
#     # likes = df.columns[2:5]
    

#     return cleanup(get_comments(filter_course, likes))

# def extract_dislikes(df, filter_course):
#     dislikes = df.columns[3]
#     # dislikes = df.columns[5:9]

#     return cleanup(get_comments(filter_course, dislikes))


def extract_likes(df, filter_course):
    likes = df.columns[2]
    # likes = df.columns[2:5]
    

    return cleanup(get_comments(filter_course, likes))

def extract_dislikes(df, filter_course):
    dislikes = df.columns[3]
    # dislikes = df.columns[5:9]

    return cleanup(get_comments(filter_course, dislikes))