#coding:utf-8

"""
    config.py
    ~~~~~~~~~~~
    配置信息 and
    一些微信定义的数据标准格式模板
"""


DEBUG = True


#文本消息格式
TEXT_TEMPLATE= """<xml>
         <ToUserName><![CDATA[%s]]></ToUserName>
         <FromUserName><![CDATA[%s]]></FromUserName>
         <CreateTime>%s</CreateTime>
         <MsgType><![CDATA[text]]></MsgType>
         <Content><![CDATA[%s]]></Content>
         </xml>"""


#图文消息格式
PICTEXT_TEMPLATE= """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>%s</ArticleCount>
            <Articles>
            %s
            </Articles>
            </xml> """


ARTICLE_ITEM="""
            <item>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[%s]]></Description>
            <PicUrl><![CDATA[%s]]></PicUrl>
            <Url><![CDATA[%s]]></Url>
            </item>
            """

#音乐消息格式
MUSIC_TEMPLATE="""
            <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[music]]></MsgType>
                <Music>
                    <Title><![CDATA[%s]]></Title>
                    <Description><![CDATA[%s]]></Description>
                    <MusicUrl><![CDATA[%s]]></MusicUrl>
                    <HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
                </Music>
            </xml>
	           """



APIKEY = '04b1ef3af394749a0e15cdb0dabd5dce'
