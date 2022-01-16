#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, sys, mysql.connector as mysql
from mysql.connector import errorcode

# Definition des arguments du plugin
parser = argparse.ArgumentParser ()
parser.add_argument("-H", "--host", type=str, default='localhost', help="Nom d'hôte ou adresse IP du serveur de base de données, localhost par défaut")
parser.add_argument("-P", "--port", type=int, default='3306', help="Spécifiez un port, 3306 par défaut (TCP uniquement)")
parser.add_argument("-u", "--user", type=str, help="Spécifiez le nom d'utilisateur autorisé à se connecter à la base de données")
parser.add_argument("-p", "--password", type=str, help="Spécifiez le mot de passe utilisateur pour se connecter à la base de données")
parser.add_argument("-d", "--dbname", type=str, help="Spécifiez le nom de la base de données à laquelle vous souhaitez vous connecter")
parser.add_argument("-w", "--warning", type=int, default='4', help="Spécifiez le seuil d'avertissement, avec un nombre de commentaires, 4 par défaut")
parser.add_argument("-c", "--critical", type=int, default='10', help="Spécifiez le seuil critique, avec un nombre de commentaires, 10 par défaut")
parser.add_argument("-i", "--interval", type=int, default='4', help="Intervalle en heures pour le comptage des commentaires, 4 par défaut")
args = parser.parse_args ()

#  Vérifiez si les arguments sont présents et les seuils sont corrects
if not args.user or not args.password or not args.dbname:
    parser.print_help()
    sys.exit(3)

elif args.critical <= args.warning:
    print(" le seuil critique ne peut pas être inférieur à l'avertissement !!!")
    sys.exit(3)

# requete qui affiche le nombre de commentaire qui ont ete  envoyé les 4 dernieres heure
query = "select COUNT(comment_ID) FROM wp_comments where comment_date >= NOW() - INTERVAL 4 HOUR"

# Établir la connexion à la base de données et exécuter la commande
try:
    cnx = mysql.connect(host=args.host, port=args.port, user=args.user, password=args.password, database=args.dbname)
    cursor = cnx.cursor(buffered=True , dictionary=True)
    cursor.execute(query)
    result=cursor.fetchall()
#    print(result[0]['COUNT(comment_ID)'])
except mysql.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("vous avez un problème de connexion avec vos identifiants")
        sys.exit(3)
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("base de données n'existe pas")
        sys.exit(3)
    else:
        print(err)
        sys.exit(3)
finally:
    cnx.close()

# Return result to Nagios
if result[0]['COUNT(comment_ID)'] >= args.critical:
    print("SPAM CRITICAL - Plus que  {} commentaires ont été posté les  {}  dernières heures !!!".format(args.critical, args.interval))
    sys.exit(2)
elif result[0]['COUNT(comment_ID)'] >= args.warning:
    print("SPAM WARNING - Plus que  {} commentaires ont été posté les  {}  dernières heures !!! ".format(args.warning, args.interval))
    sys.exit(1)
else:
    print("SPAM OK - Tout est normal  dans les  {} dernières heures .".format(args.interval))
    sys.exit(0)
