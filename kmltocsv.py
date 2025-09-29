from bs4 import BeautifulSoup
import csv
import simplejson
import requests


def convertir(fichier):
    with open(fichier, 'r') as f:
        soup = BeautifulSoup(f, features="xml")

        # After you have a soup object, you can access tags very easily.
        # For instance, you can iterate over and get <description> like so:

        i = 0
        # for node in soup.select('description'):
        #     print(node)
        #     if i > 2:
        #         break
        #     i += 1

        data = []
        for node in soup.findAll("Placemark"):
            if "civam bio 66" in node.parent.nom.text:
                cat = 1
            elif "bienvenue à la ferme" in node.parent.nom.text:
                cat = 2
            elif "hors réseaux" in node.parent.nom.text:
                cat = 2
            elif "Boutiques" in node.parent.nom.text:
                cat = 3
            elif "proximité en fruits" in node.parent.nom.text or "de plein vent" in node.parent.nom.text or "Hypermarchés" in node.parent.nom.text or "producteurs MPP" in node.parent.nom.text or "RHD" in node.parent.nom.text:
                cat = 4
                continue

            try:
                datas = node.ExtendedData.findAll("Data")
                if len(datas) > 3:
                    print ("datat > 3 cat " + str(cat))
                    prod = datas[2].text.strip() + ", " + datas[3].text.strip() if datas[3].text.strip() else datas[2].text.strip().replace("<br>", "")
                    prod = prod.replace("<br>", ", ").replace("\n", ". ")
                    try:

                        data.append({"titre" : node.nom.text.strip().lower().capitalize(), "Nom agriculteur":datas[1].text.strip(),
                                 "Production":prod,
                                 "Email":datas[6].text.strip(),
                                 #"lat2":datas[5].text.strip().split(",")[0],
                                 #"lon2":datas[5].text.strip().split(",")[1],
                                 "lat":node.Point.coordinates.text.strip().split(",")[1],
                                 "lon":node.Point.coordinates.text.strip().split(",")[0],
                                 "url":datas[7].text.strip(),
                                 "categorie":cat
                                 })
                    except:
                        pass
                elif len(datas) == 3:
                    print("datat == 3 cat " + str(cat))
                    prod = datas[0].text.strip().replace("<br>", ", ").replace("\n", ". ")
                    latlon = datas[2].text.strip().split(",")
                    try:
                        lat = float(latlon[0])
                        lon = float(latlon[1])
                    except:
                        try:
                            adresse = datas[2].text.strip().replace("\n"," ").replace(" ","-")
                            url = "https://api-adresse.data.gouv.fr/search?q=" + adresse + "&format=json"
                            reponse = requests.get(url)
                            data_geo = simplejson.loads(reponse.text)
                            lat = float(data_geo['features'][0]["geometry"]["coordinates"][1])
                            lon = float(data_geo['features'][0]["geometry"]["coordinates"][0])
                        except:
                            print ("erreur " + adresse)
                            print (url)
                            print (reponse)
                            print (data_geo)
                            print(node.nom.text)
                            continue

                    data.append({"titre" : node.nom.text.strip().lower().capitalize(), "Nom agriculteur":"",
                                 "Production":prod,
                                 "Email":"",
                                 "lat":lat,
                                 "lon":lon,
                                 "url":datas[1].text.strip(),
                                 "categorie":cat
                                 })
                else:
                    print ("datat < 3 cat " + str(cat))
                    prod = datas[0].text.strip()
                    prod = prod.replace("<br>", ", ").replace("\n", "")
                    try:
                        adresse = datas[2].text.strip()
                        url = "https://api-adresse.data.gouv.fr/search?q=" + adresse + "&format=json"
                        reponse = requests.get(url)
                        data_geo = simplejson.loads(reponse.text)
                        latitude = float(data_geo['features'][0]["geometry"]["coordinates"][1])
                        longitude = float(data_geo['features'][0]["geometry"]["coordinates"][0])
                    except:
                        try:
                            adresse = node.address.text.strip().replace("\n", " ")
                            url = "https://api-adresse.data.gouv.fr/search?q=" + adresse + "&format=json"
                            reponse = requests.get(url)
                            data_geo = simplejson.loads(reponse.text)
                            latitude = float(data_geo['features'][0]["geometry"]["coordinates"][1])
                            longitude = float(data_geo['features'][0]["geometry"]["coordinates"][0])
                        except:
                            continue

                    data.append({"titre" : node.nom.text.strip().lower().capitalize(), "Nom agriculteur":"",
                                 "Production":prod,
                                 "Email":"",
                                 #"lat2":datas[5].text.strip().split(",")[0],
                                 #"lon2":datas[5].text.strip().split(",")[1],
                                 "lat":latitude,
                                 "lon":longitude,
                                 "url":datas[1].text.strip(),
                                 "categorie":cat
                                 })
                #
                # except Exception as e:
                #     print(e)
                #     print(node)
                #if i > 4:
                #    break
                i += 1
            except Exception as e:
                print(node.parent.nom.text)
                print(node.nom.text)
                print(e)


    keys = data[0].keys()

    with open('/home/eloi/producteurs.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)



fic = "/home/eloi/producteurs.kml"
convertir(fic)
