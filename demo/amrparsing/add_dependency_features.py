import sys, re
import networkx as nx

#dep_labels = 'vmod nmod pmod p sub dep obj root vc prd amod sbar'.split()
dep_labels = map(lambda i: hex(i)[2],range(16))

def readNextDependencyParse(h):
    G = nx.DiGraph()
    readAny = False
    n = 0
    while True:
        l = h.readline()
        if l == '' or l[0] == ' ' or l.isspace():
            break
        n += 1
        a = l.strip().split(':')
        assert(len(a) == 2)
        [parent,label] = a
        assert(parent.isdigit())
        assert(label.isdigit())
        parent = int(parent)
        label = int(label)
        G.add_edge(n, parent, l=dep_labels[label-1], d='L' if parent < n else 'R')
        
    return G

def readNextAMRInput(h):
    sent = ['ROOT']
    amr  = []
    while True:
        l = h.readline()
        if l is None or l == "": break
        if l.isspace():
            if len(amr) > 0: break
            continue
        l = l.strip()
        w = l.split('|')[0].split()[-1].lower()[:4]  # only take first four characters of word
        sent.append(w)
        amr.append(l)
    return sent,amr

def vwify(k,v):
    k = k.replace(':', '*C*').replace('|', '*P*').replace(' ', '_')
    if abs(v-1.) > 1e-6: return k + ':' + str(v)
    return k

def getNodeFeatures(G, sent, n):  # this is ONE-based; assume sent[0] = '*ROOT*'
    F = {}
    def add(k,v=1.): F[k] = F.get(k,0) + v

    # neighbor features
    add('ns', len(G.successors(n)))
    add('np', len(G.predecessors(n)))
    for m in G.successors_iter(n):
        e = G.edge[n][m]
        add('s-%s%s' % (e['l'], e['d']))
        add('s-%s%s-%s' % (e['l'], e['d'], sent[m]))
    for m in G.predecessors_iter(n):
        e = G.edge[m][n]
        add('p-%s%s' % (e['l'], e['d']))
        add('p-%s%s-%s' % (e['l'], e['d'], sent[m]))

    # path to root
    try:
        path = nx.shortest_path(G, source=n, target=0)
        L    = len(path)
        cur  = 'p_'
        for l in range(L-1):
            a,b = path[l], path[l+1]
            e   = G.edge[a][b]
            cur += e['l']
            add(cur)
    except nx.exception.NetworkXNoPath:
        add('p_')
        pass

    return ' '.join(sorted([vwify(k,v) for k,v in F.iteritems() if abs(v) > 1e-6]))

def doOneAMRDep(hAMR, hDEP):
    G = readNextDependencyParse(hDEP)
    sent,amr = readNextAMRInput(hAMR)

    if len(sent) == 1 and len(G) == 0: return False
        
    if len(sent) != len(G):
        print 'failure: read sentence "%s" and graph with %d nodes' % (' '.join(sent), len(G))
    assert(len(sent) == len(G))

    for n,line in enumerate(amr):
        fts = getNodeFeatures(G, sent, n+1)
        print '%s |y %s' % (line, fts)
    print ''

    return True

def main(fileAMR, fileDEP):
    with open(fileAMR) as hAMR:
        with open(fileDEP) as hDEP:
            while doOneAMRDep(hAMR, hDEP):
                pass

if __name__ == '__main__' and len(sys.argv) > 0 and sys.argv[0] != '':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'usage: python add_dependency_features.py [amr-input-file] [dependency-prediction-file]'
    else:
        main(*sys.argv[1:])

