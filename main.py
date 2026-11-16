from redscope.cli import banner, handle_crawl, handle_api, handle_diff, handle_graph
from redscope.db import init_db

import argparse 
def main():

    print(banner)
    parse = argparse.ArgumentParser(description="Redscope - Evidence - Driven Attack Surface Intelligence")
    subparse = parse.add_subparsers(dest="command")
    subcr = subparse.add_parser("crawl", help="")
    subcr.add_argument("--target", required = True) 
    subcr.add_argument("--project", default = "Default")
    subcr.add_argument("--max-pages", type = int, default = 10)
    subcr.add_argument("--max-depth", type = int, default = 2)

    subdiff = subparse.add_parser("diff", help="compare 2 scans for attack surface drift")
    subdiff.add_argument("--baseline", type = int, required = True)
    subdiff.add_argument("--current", type = int, required = True)

    subapi = subparse.add_parser("import-api", help="Import OpenAPI / Swagger specification")
    subapi.add_argument("--file", required = True)
    subapi.add_argument("--project", default = "Default")

    subgraph = subparse.add_parser("graph", help="generate attack surface graph")
    subgraph.add_argument("--scan", type = int, required = True)
    subgraph.add_argument("--output", default=None)

    args = parse.parse_args()
    if not args.command:
        parse.print_help()
        return 
    conn = init_db()
    try: 
        if args.command == "crawl":
            handle_crawl(conn, args)
        elif args.command == "diff":
            handle_diff(conn, args)
        elif args.command == "graph":
            handle_graph(conn, args)
        elif args.command == "import-api":
            handle_api(conn, args)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

