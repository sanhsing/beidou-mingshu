"""SEO Meta 組件 | @璃語"""
def get_seo_meta(title, desc, url="", image=""):
    return f'''
    <meta name="description" content="{desc}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{image or '/static/og-image.png'}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="{url}">
    '''
