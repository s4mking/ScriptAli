import json
import requests
import re
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import time


def getLastIdAddOne(connection):
    cursor = connection.cursor(buffered=True)
    select = "SELECT id from usrflacaposts ORDER BY id DESC LIMIT 1"
    cursor.execute(select)
    return cursor.fetchone()[0] + 1

def findIdPostByType(connection, name, type):
    cursor = connection.cursor(buffered=True)
    select = "SELECT id FROM usrflacaposts WHERE usrflacaposts.post_title = %s AND usrflacaposts.post_type = %s "
    cursor.execute(select, (name, type))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def findIdTermByType(connection, name):
    cursor = connection.cursor(buffered=True)
    select = "SELECT term_id FROM wp_terms WHERE wp_terms.name = %s"
    cursor.execute(select, (name,))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def findIfSameMetaNameWithSamePostId(connection, postId, metaname):
    cursor = connection.cursor(buffered=True)
    select = "SELECT meta_id FROM wp_postmeta WHERE J6e0wfWFh_postmeta.post_id = %s AND J6e0wfWFh_postmeta.meta_key = %s "
    cursor.execute(select, (postId, metaname))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def findIfSameMetaGedNameWithSamePostId(connection, postId, metaname):
    cursor = connection.cursor(buffered=True)
    select = "SELECT meta_id FROM usrflacapostmeta WHERE usrflacapostmeta.post_id = %s AND usrflacapostmeta.meta_key = %s "
    cursor.execute(select, (postId, metaname))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def createPostWpPostAndReturnId(connection, actualTime, row):
    queryPost = "INSERT INTO usrflacaposts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, guid, post_type) VALUES (%(post_author)s, %(post_date)s, %(post_date_gmt)s, %(post_content)s, %(post_title)s, %(post_excerpt)s, %(post_name)s, %(to_ping)s, %(pinged)s, %(post_modified)s, %(post_modified_gmt)s, %(post_content_filtered)s, %(guid)s, %(post_type)s)"
    lastId = getLastIdAddOne(connection)
    postContent = {
        "post_author": 1,
        "post_date": actualTime,
        "post_date_gmt": actualTime,
        "post_content": row['product_description'],
        "post_title": row['product_name'],
        "post_excerpt": "",
        "to_ping": "",
        "pinged": "",
        "post_name": row['product_alias'],
        "post_modified": actualTime,
        "post_modified_gmt": actualTime,
        "post_content_filtered": "",
        "guid": "http://ali.local/?post_type=product&#038;p="
        + str(lastId),
        "post_type": "product",
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryPost, postContent)
    connection.commit()
    return cursor.lastrowid

def createPostType(connection, actualTime, data, postType):
    queryContactSynaPost = "INSERT INTO usrflacaposts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, guid, post_type) VALUES (%(post_author)s, %(post_date)s, %(post_date_gmt)s, %(post_content)s, %(post_title)s, %(post_excerpt)s, %(post_name)s, %(to_ping)s, %(pinged)s, %(post_modified)s, %(post_modified_gmt)s, %(post_content_filtered)s, %(guid)s, %(post_type)s)"
    lastId = getLastIdAddOne(connection)
    postContent = {
        "post_author": 1,
        "post_date": actualTime,
        "post_date_gmt": actualTime,
        "post_content": '',
        "post_title": data,
        "post_excerpt": "",
        "to_ping": "",
        "pinged": "",
        "post_name": data,
        "post_modified": actualTime,
        "post_modified_gmt": actualTime,
        "post_content_filtered": "",
        "guid": "http://ali.local/?post_type="+postType+"&#038;p="
        + str(lastId),
        "post_type": postType,
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryContactSynaPost, postContent)
    connection.commit()
    return cursor.lastrowid

def createCatAndReturnId(connection, actualTime, cat):
    queryContactSynaPost = "INSERT INTO usrflacaterms (name, slug, term_group) VALUES (%(name)s, %(slug)s, %(term_group)s)"
    lastId = getLastIdAddOne(connection)
    postContent = {
        "name": cat['category_name'],
        "slug": cat['category_namekey'],
        "term_group": 0,
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryContactSynaPost, postContent)
    connection.commit()
    return cursor.lastrowid

def findIfindRelationshipsdTermTaxonomy(connection, object_id,term_taxonomy_id):
    cursor = connection.cursor(buffered=True)
    select = "SELECT * FROM usrflacaterm_relationships WHERE wp_term_relationships.object_id = %s AND wp_term_relationships.term_taxonomy_id = %s"
    cursor.execute(select, (object_id,term_taxonomy_id))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def acreateTaxonomyAndReturnId(connection, cat):
    queryTaxonomyPost = "INSERT INTO usrflacaterm_taxonomy (term_id, taxonomy, description, parent, count) VALUES (%(term_id)s, %(taxonomy)s, %(description)s, %(parent)s, %(count)s)"
    postContent = {
        "term_id": cat,
        "taxonomy": 'product_cat',
        "description": '',
        "parent": 0,
        "count": 0
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryTaxonomyPost, postContent)
    connection.commit()
    

def createTermRelationship(connection, cat, product):
    queryTaxonomyPost = "INSERT INTO usrflacaterm_relationships (object_id, term_taxonomy_id, term_order) VALUES (%(object_id)s, %(term_taxonomy_id)s, %(term_order)s)"
    postContent = {
        "object_id": product,
        "term_taxonomy_id": cat,
        "term_order": 0,
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryTaxonomyPost, postContent)
    connection.commit()
    return cursor.lastrowid


def createPostMeta(connection, entry, meta_key, id):
    cursor = connection.cursor(buffered=True)
    query_postmetamember = "INSERT INTO usrflacapostmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)"
    meta_value = entry
    cursor.execute(
        query_postmetamember,
        (id, meta_key, meta_value),
    )
    connection.commit()

def createPostMetaGed(connection, entry, meta_key, id):
    cursor = connection.cursor(buffered=True)
    query_postmetamember = "INSERT INTO usrflacapostmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)"
    meta_value = entry
    cursor.execute(
        query_postmetamember,
        (id, meta_key, meta_value),
    )
    connection.commit()

def updatePostMetaGed(connection, entry, meta_key, id):
    cursor = connection.cursor(buffered=True)
    query_postmetamember = "UPDATE usrflacapostmeta SET meta_value = %s  WHERE post_id = %s AND meta_key = %s"
    meta_value = entry
    cursor.execute(
        query_postmetamember,
        (meta_value, id, meta_key),
    )
    connection.commit()

def updatePostMeta(connection, entry, meta_key, id):
    cursor = connection.cursor(buffered=True)
    query_postmetamember = "UPDATE usrflacapostmeta SET meta_value = %s  WHERE post_id = %s AND meta_key = %s"
    meta_value = entry
    cursor.execute(
        query_postmetamember,
        (meta_value, id, meta_key),
    )
    connection.commit()

def connectDatabase():
    try:
        local = {
            "host": "127.0.0.1",
            "database": "local",
            "user": "root",
            "password": "password",
            "port": 10010,
        }

        dev = {
            "host": "localhost",
            "database": "freudlacan",
            "user": "usrflaca",
            "password": "0dsY%0v95",
            "port": 3306,
        }

        connection = mysql.connector.connect(
            host=dev["host"],
            database=dev["database"],
            user=dev["user"],
            password=dev["password"],
            port=dev["port"],
        )

        return connection
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)



def launchProductsAndCategoriesInsertion():
    connection = connectDatabase()

    # Opening JSON file
    f = open('hikashop_product.json')
    
    # returns JSON object as
    # a dictionary
    dataProducts = json.load(f)
    
    # Iterating through the json
    # list
    actualTime = time.strftime("%Y-%m-%d %H:%M:%S")
    dictProductsIds = {}
    for row in dataProducts:
        idPost = createPostWpPostAndReturnId(connection, actualTime, row)
        createPostMeta(connection, row['product_sort_price'], '_price', idPost)
        createPostMeta(connection, row['product_sort_price'], '_sale_price', idPost)
        createPostMeta(connection, row['product_code'], '_sku', idPost)
        dictProductsIds[row['product_id']]=row['product_name']
    
    cats = open('cats_hika.json')
    dataCats = json.load(cats)
    dictCatsIds = {}
    for cat in dataCats:
        idPost = createCatAndReturnId(connection, actualTime, cat)
        idTaxonomy = acreateTaxonomyAndReturnId(connection, idPost)
        dictCatsIds[cat['category_id']]=cat['category_name']

    catsProducts = open('hikashop_product_category.json')
    dataCatsProducts = json.load(catsProducts)
    for catProduct in dataCatsProducts:
        catProduct['product_category_id']
        catName = dictCatsIds[catProduct['category_id']]
        productName = dictProductsIds[catProduct['product_id']]
        idProduct = findIdPostByType(connection, productName, 'product')
        idCat = findIdTermByType(connection, catName)
        if not findIfindRelationshipsdTermTaxonomy(connection, idProduct, idCat):
            createTermRelationship(connection, idCat, idProduct)
        
    # Closing file
    f.close()

class Document:
    # List out all possible attributes
    ALL_ATTRIBUTES = [
        "Nom", "Extension", "Chemin", "DateCreated", "DateModified",
        "numorder", "hitcount", "TitreDocument", "SousTitre", "AuteurDocument",
        "Rubrique", "Dossier", "SousDossier", "Tag", "Ouvrage", "Annee", "Pages",
        "Editeur", "Ville", "Resume", "Introduction", "DatePublication",
        "EtatDocument", "interDBZEDOC", "Origine", "AncienIdentifiant",
        "MediaIntroduction", "ReserveMembre", "Vedette", "secure", "zedate"
    ]  # you can add/remove based on your JSON structure

    def __init__(self, **kwargs):
        for attr in Document.ALL_ATTRIBUTES:
            setattr(self, attr, kwargs.get(attr, ""))

def launchGedIndexation():
    connection = connectDatabase()
    actualTime = time.strftime("%Y-%m-%d %H:%M:%S")
    unique_tags = set()
    f = open('csvjson.json')
    gedItems = json.load(f)
    document_objects = []
    for entry in gedItems:
        document = Document(**entry)
        document_objects.append(document)
        tags = entry['Tag'].split(',')
        unique_tags.update(tags)
    tag_list = list(unique_tags)
    tag_list = [tag.strip() for tag in tag_list if tag.strip() != ""]
    tag_to_id = {}
    for tag in tag_list:
        id = createPostType(connection,actualTime, tag, "tag")
        tag_to_id[tag] = id
    for entry in document_objects:
        idGedDoc = createPostType(connection,actualTime, entry.Nom, "documents-ged")
        for attr in Document.ALL_ATTRIBUTES:
            attribute_value = getattr(entry, attr)
            """ print(entry.attribute_value) """
            if (
                findIfSameMetaGedNameWithSamePostId(
                    connection, idGedDoc, attr
                )
                is None
            ):
                createPostMetaGed(
                    connection,
                    attribute_value,
                    attr,
                    idGedDoc,
                )
            else:
                updatePostMetaGed(
                    connection,
                    attribute_value,
                    attr,
                    idGedDoc,
                )
    print(tag_to_id)
    #for document in document_objects:
        #print(document.Tag)

launchProductsAndCategoriesInsertion()
# launchGedIndexation()