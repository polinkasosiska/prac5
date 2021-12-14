import zlib
import graphviz
import sys



repo_path = sys.argv[1]

def get_content(sha):
    folder = sha[:2]
    name = sha[2:]
    path = repo_path + '/.git/objects/' + folder + '/' + name
    f = open(path, 'rb').read()
    bin_str = zlib.decompress(f)
    return bin_str

def split_tree_into_files(tree_content):
    files = []

    files_string = tree_content.split(b'\x00', maxsplit=1)[1]

    while len(files_string) > 0:
        parts = files_string.split(maxsplit=1)[1].split(b'\x00', maxsplit=1)
        file_name = parts[0].decode('utf-8')
        sha = parts[1][:20].hex()
        files_string = parts[1][20:]
        files.append({'file_name': file_name, 'sha': sha})
    return files

def add_tree(tree, parent_id):
    tree_content = get_content(tree)
    files = split_tree_into_files(tree_content)

    for i in range(len(files)):
        file_name = files[i]['file_name']
        sha = files[i]['sha']
        id = files[i]['sha'] + file_name

        type = get_content(sha).split()[0].decode('utf-8')

        if type == 'tree':
            graph.node(id, file_name, shape='doublecircle')
        else:
            graph.node(id, file_name, shape='circle')
        graph.edge(parent_id, id)

        if type == 'tree':
            add_tree(sha, id)
        else:
            content = get_content(sha)
            text = content.split(maxsplit=1)[1].split(b'\x00', maxsplit=1)[1].decode('utf-8')
            if len(text) > 0:
                graph.node(id + 'text', text)
                graph.edge(id, id + 'text')


graph = graphviz.Digraph(format='png', strict=True)

head = open(repo_path + '/.git/logs/HEAD')
lines = head.readlines()

for i in range(len(lines)):
    parent = lines[i][:40]
    commit = lines[i][41:81]
    name = lines[i].split()[-1]

    graph.node(commit, name, shape='square')
    
    if (parent != '0'*40):
        graph.edge(parent, commit)

    commit_content = get_content(commit).decode('utf-8')
    tree = commit_content.split()[2][:40]
    
    add_tree(tree, commit)
    

graph.render('output.gv', view=True)




















