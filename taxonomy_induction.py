import sys
import networkx as nx

def clean_webIsALod(input_file):
    output_file = "cleaned_data.txt"
    final_file = "processed_data.txt"
    f1 = open(input_file, "r", encoding="utf8")
    f2 = open(output_file, "w", encoding="utf8")

    for line in f1.readlines():

        #remove unnecessary charaacters and spaces and split the lines into hyponyms, hypernyms and confidence values

        comps = line.rstrip().rsplit(";")
        hyponym = comps[0].replace("_"," ").replace("%2F"," ").replace("+"," ").replace("%3E"," ").replace("%27","").replace("%3D","").replace("%24","").replace("%2B"," ").replace("%3C","").replace("%5D"," ").strip()
        hypernym = comps[1].rsplit("\t")[0].replace("_"," ").replace("+"," ").replace("%3D"," ").strip()
        conf = comps[1].rsplit("\t")[1]

        if float(conf) > 0.3 and hyponym!="" and hyponym[0]!="%":
            f2.write(str(hyponym) + "\t" + str(hypernym) + "\t" + str(conf) + "\n")

    f1.close()
    f2.close()

    f3 = open(output_file, "r", encoding="utf8")
    f4 = open(final_file, "w", encoding="utf8")

    #sort the cleaned data

    lines = sorted(f3.readlines())
    for line in lines:
        f4.write(line)

    f3.close()
    f4.close()
    
    return final_file


def highest_confidence(req_hyponym, processed_data):

    #function that returns the hypernym with the highest confidence value from processed_data.txt

    fin = open(processed_data, "r", encoding="utf8")
    conf_list = []
    hyper_list = []
    hyper = ""

    for item in fin.readlines():
        comps = item.rsplit("\t")
        hyponym = comps[0].strip()
        hypernym = comps[1].strip()
        conf = comps[2].strip()

        if req_hyponym == hyponym:
            conf_list.append(conf)
            hyper_list.append(hypernym)
            
    if len(conf_list)!=0:
        max_conf = max(conf_list)
        ind = conf_list.index(max_conf)
        hyper = hyper_list[ind]
    
    fin.close()

    return hyper


def taxonomy_induction(input_file, processed_data):

    fin1 = open(input_file, "r", encoding="utf8")
    entities = []
    
    G = nx.DiGraph()

    for line in fin1.readlines():
        entities.append(line.strip())

    #ind=0
    for ind in range(0,35):
    #while len(G.nodes) < 50:
        G.add_node(entities[ind])
        hyper = highest_confidence(entities[ind], processed_data)
        if hyper == "": #if a node does not have a hypernym as parent, connect it to the root
            G.add_edge(entities[ind], "Entity")
        else:
            G.add_edge(entities[ind], hyper, length=1000)
            if hyper not in entities:
                entities.append(hyper)
        #ind=ind+1

    G.remove_edges_from(nx.selfloop_edges(G))

    for node in G.nodes:
        if len(list(G.successors(node)))==0 and node != "Entity":
            G.add_edge(node, "Entity")
    
    p = nx.drawing.nx_pydot.to_pydot(G)
    p.write_png("taxonomy.png")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Expected exactly 1 argument: input file")
    #processed_data = clean_webIsALod("webisalod-pairs.txt")
    processed_data = "processed_data.txt"
    taxonomy_induction(sys.argv[1], processed_data)


#References:
#https://networkx.org/documentation/stable/tutorial.html
#https://stackoverflow.com/questions/49427638/removing-self-loops-from-undirected-networkx-graph
#https://networkx.org/documentation/stable/reference/drawing.html
#https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3
