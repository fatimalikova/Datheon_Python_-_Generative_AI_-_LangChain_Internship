import sys

from task2_rag.rag_pipeline import answer, build_vectorstore


def main():
    rebuild = "--rebuild" in sys.argv
    print("Sənədlər indekslənir...")
    store = build_vectorstore(rebuild=rebuild)
    print("Hazırdır. Çıxmaq üçün 'exit' yaz.\n")

    while True:
        q = input("Sual: ").strip()
        if q.lower() in {"exit", "quit", ""}:
            break
        text, sources = answer(q, store)
        print(f"\nCavab: {text}")
        print("Mənbələr:", ", ".join(sources), "\n")


if __name__ == "__main__":
    main()