
# 使用StatisticsWithPrivacy类的统一接口
from tools.StatisticsWithPrivacy import StatisticsWithPrivacy


def getStatistics(postData) -> object:
    mechanism = postData['mechanism']        # 由于机制目前只有laplace机制,所以此参数暂时无用
    searchWay = postData['searchWay']['way']
    params = postData['searchWay']['params']
    attr = postData['searchWay']['attr']
    filename = postData['filename']

    sp = StatisticsWithPrivacy(filename, attr, params)
    # 计算隐私值
    evalString_private = 'sp.private_{0}()'.format(searchWay)
    privateRes = eval(evalString_private)
    # 计算真实值
    evalString = 'sp.{0}()'.format(searchWay)
    res = float(eval(evalString))
    return {'res': res, 'privateRes': privateRes}

def getHistogramData(df):
    a = df['carrots_eaten'].hist(bins=10)
    heights = [a.patches[i]._height for i in range(10)]
    width = a.patches[0]._width
    x0 = [a.patches[i].xy for i in range(10)]
    histData = [{'x0': x0[i][0], 'x1': x0[i][0] + width, 'height': heights[i]} for i in range(10)]
    return histData
