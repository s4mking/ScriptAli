import json
import requests
import re
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import time
import sys
import os
import csv
import magic


def getLastIdAddOne(connection):
    cursor = connection.cursor(buffered=True)
    select = "SELECT id from usrflacaposts ORDER BY id DESC LIMIT 1"
    cursor.execute(select)
    return cursor.fetchone()[0] + 1

def getLastIdTranslationAddOne(connection):
    cursor = connection.cursor(buffered=True)
    select = "SELECT trid from usrflacaicl_translations ORDER BY trid DESC LIMIT 1"
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
    select = "SELECT term_id FROM usrflacaterms WHERE usrflacaterms.name = %s"
    cursor.execute(select, (name,))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def findIfSameMetaNameWithSamePostId(connection, postId, metaname):
    cursor = connection.cursor(buffered=True)
    select = "SELECT meta_id FROM usrflacapostmeta WHERE usrflacapostmeta.post_id = %s AND usrflacapostmeta.meta_key = %s "
    cursor.execute(select, (postId, metaname))
    result = cursor.fetchone()
    return result[0] if result is not None else None

def findIfSameMetaGedNameWithSamePostId(connection, postId, metaname):
    cursor = connection.cursor(buffered=True)
    select = "SELECT meta_id FROM usrflacapostmeta WHERE usrflacapostmeta.post_id = %s AND usrflacapostmeta.meta_key = %s "
    cursor.execute(select, (postId, metaname))
    result = cursor.fetchone()
    return result[0] if result is not None else None


def findSameTag(connection, name):
    cursor = connection.cursor(buffered=True)
    select = "SELECT ID FROM usrflacaposts WHERE usrflacaposts.post_title = %s "
    cursor.execute(select, ([name]))
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
        "guid": "https://dev.freud-lacan.com/?post_type=product&#038;p="
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
        "post_title": data[:254],
        "post_excerpt": "",
        "to_ping": "",
        "pinged": "",
        "post_name": data[:200],
        "post_modified": actualTime,
        "post_modified_gmt": actualTime,
        "post_content_filtered": "",
        "guid": "https://dev.freud-lacan.com/?post_type="+postType+"&#038;p="
        + str(lastId),
        "post_type": postType,
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryContactSynaPost, postContent)
    connection.commit()
    return cursor.lastrowid

def createPostTypeAttachment(connection, actualTime, title, name, postType, mimeType, idParent, extension):
    queryContactSynaPost = "INSERT INTO usrflacaposts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_mime_type, guid, post_type, post_parent) VALUES (%(post_author)s, %(post_date)s, %(post_date_gmt)s, %(post_content)s, %(post_title)s, %(post_excerpt)s, %(post_name)s, %(to_ping)s, %(pinged)s, %(post_modified)s, %(post_modified_gmt)s, %(post_content_filtered)s, %(post_mime_type)s, %(guid)s, %(post_type)s, %(post_parent)s)"
    lastId = getLastIdAddOne(connection)
    postContent = {
        "post_author": 1,
        "post_date": actualTime,
        "post_date_gmt": actualTime,
        "post_content": '',
        "post_title": title,
        "post_excerpt": "",
        "to_ping": "",
        "pinged": "",
        "post_name": name,
        "post_modified": actualTime,
        "post_modified_gmt": actualTime,
        "post_content_filtered": "",
        "post_mime_type": mimeType,
        "guid": ("https://dev.freud-lacan.com/wp-content/themes/freudlacan-front/assets/content/2023/09/"+name+'.'+extension),
        "post_type": postType,
        "post_parent": idParent,
    }
    cursor = connection.cursor(buffered=True)
    cursor.execute(queryContactSynaPost, postContent)
    connection.commit()
    return cursor.lastrowid

def updatePostContentDocumentGed(connection, name, extension, id):
    cursor = connection.cursor(buffered=True)
    query_postmetamember = "UPDATE usrflacaposts SET post_content = %s  WHERE ID = %s"
    meta_value = f"<a href='https://dev.freud-lacan.com/wp-content/themes/freudlacan-front/assets/content/2023/09/{name}.{extension}'>{name}</a>"
    cursor.execute(
        query_postmetamember,
        (meta_value, id),
    )
    connection.commit()

def createPostTranslation(connection, idPost):
    queryContactSynaPost = "INSERT INTO usrflacaicl_translations (element_type, element_id, trid, language_code) VALUES (%(element_type)s, %(element_id)s, %(trid)s, %(language_code)s)"
    lastId = getLastIdTranslationAddOne(connection)
    postContent = {
        "element_type": 'post_product',
        "element_id": str(idPost),
        "trid": str(lastId),
        "language_code": 'fr',
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
    select = "SELECT * FROM usrflacaterm_relationships WHERE usrflacaterm_relationships.object_id = %s AND usrflacaterm_relationships.term_taxonomy_id = %s"
    cursor.execute(select, (object_id,term_taxonomy_id))
    result = cursor.fetchone()
    return result[0] if result is not None else None


def findIfindRelationshipsdCat(connection, cat):
    cursor = connection.cursor(buffered=True)
    select = "SELECT * FROM usrflacaterms WHERE usrflacaterms.name = %s AND usrflacaterms.slug = %s"
    cursor.execute(select, (cat['category_name'], cat['category_namekey']))
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
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "dev":
            credentials = {
            "host": "127.0.0.1",
            "database": "local",
            "user": "root",
            "password": "password",
            "port": 10010,
        }
        elif arg == "prod":
            credentials = {
                "host": "localhost",
                "database": "freudlacan",
                "user": "usrflaca",
                "password": "0dsY%0v95",
                "port": 3306,
            }
    try:     
        connection = mysql.connector.connect(
            host=credentials["host"],
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
            port=credentials["port"],
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
        createPostTranslation(connection, idPost)
        createPostMeta(connection, row['product_sort_price'], '_price', idPost)
        createPostMeta(connection, row['product_sort_price'], '_sale_price', idPost)
        createPostMeta(connection, row['product_code'], '_sku', idPost)
        dictProductsIds[row['product_id']]=row['product_name']
    
    cats = open('cats_hika.json')
    dataCats = json.load(cats)
    dictCatsIds = {}
    for cat in dataCats:
        if not findIfindRelationshipsdCat(connection, cat):
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

def createOrUpdateMetaData(connection, idGedDoc, attribute_value, attr):
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
    arrayFileName = []
    countFile =0
    countNotFound=0
    #permet de frounir un fichier complet au client avec l'export des tags/gilename/dossier/rubrique/etc...
    with open('exportGed.csv', mode='w', encoding='utf-8', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(["Titre", "Tag", "Auteur", "Date", "Filename", "Dossier", "SousDossier", "Rubrique"])
        mime = magic.Magic(mime=True)
        fields = [
                "Nom", "Extension", "Chemin", "DateCreated", "DateModified",
                "numorder", "hitcount", "TitreDocument", "SousTitre", "AuteurDocument",
                "Rubrique", "Dossier", "SousDossier", "Tag", "Ouvrage", "Annee", "Pages",
                "Editeur", "Ville", "Resume", "Introduction", "DatePublication",
                "EtatDocument", "interDBZEDOC", "Origine", "AncienIdentifiant",
                "MediaIntroduction", "ReserveMembre", "Vedette", "secure", "zedate"
                 ]
        values = [
        "titre", "Extension", "Chemin", "DateCreated", "DateModified",
        "numorder", "hitcount", "TitreDocument", "SousTitre", "auteur",
        "rubrique", "dossier", "SousDossier", "Tag", "ouvrage", "annee", "Pages",
        "editeur", "Ville", "resume", "introduction", "date-de-publication",
        "etat-document", "interDBZEDOC", "Origine", "AncienIdentifiant",
        "media-introduction", "acces-reserve-au-membres", "mise-en-avant", "secure", "zedate"
        ]
        field_value_mapping = dict(zip(fields, values))
        for entry in document_objects:
            if len(str(entry.Nom)) > 163:
                countFile = countFile+1
            else:
                if 'Index Bibliotheque' not in entry.Chemin:
                    fileName = entry.Chemin.split("\\")[-1]
                    arrayFileName.append(fileName)
                    count=count+1
                    idGedDoc = createPostType(connection,actualTime, str(entry.TitreDocument), "documents-ged")
                    #Tag confirmé avec le client
                    if entry.SousDossier == 'Dossier de préparation' or entry.SousDossier == 'En transcription':
                        tag = 'Divers'
                    if entry.Dossier ==  'Billets d\'actualité':
                        tag = 'Billets d\'actualité'
                    if entry.Dossier == "Dossier préparatoire aux journées du 7-8 décembre 2019" or entry.Dossier == "Joyce et Nora : un vrai couple ?" or  entry.Dossier == "Retour des journées : Où donc suis-je chez moi ? Mars 2018":
                        tag = 'Archives journées d’étude'
                    if entry.Dossier == "Le collège de l'ALI":
                        tag = 'Le collège de l\'ALI'
                    if entry.Dossier == "LES CARTELS DE L'ALI":
                        tag = 'Archives journées des cartels'
                    if entry.Dossier == "Les séminaires d'hiver":
                        tag = 'Archives séminaires d’hiver'
                    if entry.Dossier == "Préparation au séminaire d'été 2021 : L'Identification" or  entry.Dossier == "Préparation au séminaire d'été 2023 : étude du séminaire XX de J. Lacan Encore":
                        tag = 'Archives séminaires d’été'
                    if entry.Dossier == "Traduction éditoriaux":
                        tag = 'Archives séminaires d’hiver'
                    if entry.Dossier == "Cartel Franco Brésilien de Psychanalyse":
                        tag = 'Cycles de conférence'
                    if entry.Dossier == "La topologie":
                        tag = 'Topologie'
                    if entry.Rubrique == "Actualités des travaux de l'ALI, Enseignements":
                        tag = ' Collège des enseignements'
                    if entry.Rubrique == "Actualités des travaux de l'ALI, Séminaire d'Été":
                        tag = ' Archives séminaires d’été'
                    if entry.Rubrique == "Billets d'actualité":
                        tag = 'Divers'
                    if entry.Dossier == "Billets d'actualité":
                        tag = 'Divers'
                    if entry.Rubrique == "Cabinet de lecture":
                        tag = 'Divers'
                    if entry.Rubrique == "Cartel franco-brésilien de la psychanalyse":
                        tag = 'Cycles de conférence'
                    if entry.Rubrique == "Controverses":
                        tag = 'Billets d’actualité'
                    if entry.Rubrique == "D'autres scènes" or entry.Rubrique == "D'autres scènes, Séminaire d'Été":
                        tag = 'D\'autres scènes'
                    if entry.Rubrique == "Éditoriaux":
                        tag = 'Éditoriaux'
                    if entry.Dossier == "Traduction éditoriaux":
                        tag = 'Éditoriaux'
                    if entry.Rubrique == "Enseignements" or entry.Rubrique ==  "ENSEIGNEMENTS 2018-2019":
                        tag = 'Collège des enseignements'
                    if entry.Rubrique == "Exercices de topologie clinique":
                        tag = 'Topologie'
                    if entry.Rubrique == "Grand Séminaire de l'ALI":
                        tag = 'Le Grand Séminaire'
                    if entry.Rubrique == "Hommage":
                        tag = 'Hommages'
                    if entry.Rubrique == " Journées d'études":
                        tag = 'Archives journées d’étude'
                    if entry.Dossier == "Séminaire d'été 2016" or entry.Dossier == "Séminaire d'été 2017":
                        tag = 'Archives séminaires d’été'
                    if entry.Rubrique == "L'histoire de l'ALI":
                        tag = 'Qui sommes-nous ?'
                    if entry.Rubrique == "Les cartels de l'ALI":
                        tag = 'Archives journées des cartels'
                    if entry.Rubrique == "Lire Freud et Lacan":
                        tag = 'Divers ?'
                    if entry.Rubrique == "Lire Freud et Lacan, Notes de lecture" or entry.Rubrique == "Notes de lecture":
                        tag = 'Notes de lecture'
                    if entry.Rubrique == "Parutions":
                        tag = 'Base documentaire'
                    if entry.Rubrique == "Psychanalyse et psychiatrie":
                        tag = 'Divers'
                    if entry.Rubrique == "Séminaire d'hiver":
                        tag = 'Archives séminaires d’hiver'
                    if entry.Rubrique == "Séminaire d'Été":
                        tag = 'Archives séminaires d’été'
                    if entry.Rubrique == "Séminaire de Charles Melman":
                        tag = 'Rue des archives => séminaires'
                    if entry.Rubrique == "Une journée avec...":
                        tag = 'Archives journées d’étude'
                    if entry.Rubrique == "États généreux (2018)":
                        tag = 'Archives journées d’étude'
                    if entry.Dossier == "Les séminaires de Charles Melman":
                        tag = 'Rue des archives => séminaires'
                    writer.writerow([entry.TitreDocument, tag if tag else '', entry.AuteurDocument, entry.DatePublication, entry.Chemin, entry.Dossier, entry.SousDossier, entry.Rubrique])
                    if tag:
                        arrayTags = []
                        id = findSameTag(connection, tag) if findSameTag(connection, tag) is not None else createPostType(connection, actualTime, tag, "tag")
                        arrayTags.append(id)
                        result = ";".join(
                            [
                                f'i:{i};s:{len(str(value))}:"{value}"'
                                for i, value in enumerate(arrayTags)
                            ]
                        )
                        result += ";"
                        metaDirigeants = {
                            "meta_key": "tag",
                            "meta_value": f"a:{len(arrayTags)}:{{{result}}}",
                        }
                        createOrUpdateMetaData(connection,idGedDoc,metaDirigeants["meta_value"],metaDirigeants["meta_key"])
                    for attr in Document.ALL_ATTRIBUTES:
                        attribute_value = getattr(entry, attr)
                        attr = field_value_mapping.get(attr, None)
                        createOrUpdateMetaData(connection,idGedDoc,attribute_value,attr)
                    #Les fichiers de la GED doivent être mis dans le dossier : ../wp-content/themes/freudlacan-front/assets/content/2023/09/
                    if not os.path.isfile('../wp-content/themes/freudlacan-front/assets/content/2023/09/'+entry.Chemin.split("\\")[-1]):
                        countNotFound=countNotFound+1
                        continue
                    #mimeType = mime.from_file('aliDocs/'+entry.Chemin.split("\\")[-1])
                    mimeType = mime.from_file('../wp-content/themes/freudlacan-front/assets/content/2023/09/'+entry.Chemin.split("\\")[-1])
                    
                    idAttachment = createPostTypeAttachment(connection, actualTime, entry.TitreDocument , str(entry.Nom), 'attachment', mimeType, idGedDoc,entry.Chemin.rsplit('.', 1)[-1])
                    createOrUpdateMetaData(connection, idAttachment, '_wp_attached_file','2023/09/'+ entry.Chemin.split("\\")[-1])
                    updatePostContentDocumentGed(connection,str(entry.Nom) ,  entry.Chemin.rsplit('.', 1)[-1] , idGedDoc)

    # Directory path where the files are located
    source_dir = "/Users/samuel/Local Sites/ali/app/public/script/aliDocs"  # Replace with the actual source directory path

    # Destination directory path
    destination_dir = "/Users/samuel/Local Sites/ali/app/public/script/aliDocsExcluded"


    # for filename in os.listdir(source_dir):
    #     source_file_path = os.path.join(source_dir, filename)
    #     if os.path.isfile(source_file_path) and filename not in arrayFileName:
    #         destination_file_path = os.path.join(destination_dir, filename)
    #         os.rename(source_file_path, destination_file_path)
    #         print(f"Moved '{filename}' to '{destination_file_path}'")
    #     # for document in document_objects:
        #     print(document.Tag)

#En commentaires pour l'instant vu que les images ont été rajouté à la main
#launchProductsAndCategoriesInsertion()
launchGedIndexation()
