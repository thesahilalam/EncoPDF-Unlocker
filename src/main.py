import os, sys, time, requests, multiprocessing
from concurrent.futures import ProcessPoolExecutor
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskProgressColumn

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils, attacks

console = Console()

def get_cpu_info():
    total = multiprocessing.cpu_count()
    optimal = max(1, int(total * 0.8))
    return total, optimal

def get_session(mode_name):
    path = f"sessions/{mode_name}.ptr"
    if os.path.exists(path):
        with open(path, 'r') as f: return int(f.read().strip())
    return 0

def save_session(mode_name, count):
    with open(f"sessions/{mode_name}.ptr", 'w') as f: f.write(str(count))

def main_menu():
    total_cpu, optimal_cpu = get_cpu_info()
    utils.display_banner(total_cpu, optimal_cpu)
    
    console.print("\n1. Brute Force | 2. Wordlist | 3. Aadhaar | 4. E-PAN | 0. Exit")
    choice = Prompt.ask("Select", choices=["0", "1", "2", "3", "4"])
    if choice == "0": sys.exit()

    pdf_path = utils.clean_path(Prompt.ask("[green]Drag PDF[/green]"))
    if not os.path.exists(pdf_path): return

    mode_map = {"1": "brute", "2": "wordlist", "3": "aadhaar", "4": "epan"}
    session_key = mode_map[choice]
    skip_val = get_session(session_key)

    if skip_val > 0:
        if Prompt.ask(f"Resume from {skip_val}?", choices=["y", "n"]) == "y": pass
        else: skip_val = 0

    if choice == "1":
        c = Prompt.ask("1.Num, 2.Alpha, 3.Mix", choices=["1","2","3"])
        mi = int(Prompt.ask("Min", default="1"))
        ma = int(Prompt.ask("Max", default="10"))
        gen_func = lambda: attacks.brute_force_gen(c, mi, ma, skip_val)
    elif choice == "2":
        if Prompt.ask("1.RockYou 2.Custom", choices=["1","2"]) == "1":
            path = "wordlists/rockyou.txt"
            if not os.path.exists(path):
                r = requests.get("https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt")
                with open(path, 'wb') as f: f.write(r.content)
        else: path = utils.clean_path(Prompt.ask("Wordlist Path"))
        gen_func = lambda: attacks.dictionary_gen(path, skip_val)
    elif choice == "3":
        n = Prompt.ask("Name", default="")
        gen_func = lambda: attacks.aadhaar_gen(n, skip_val)
    else:
        gen_func = lambda: attacks.epan_gen(skip_val)

    found = None
    tested = skip_val
    start_t = time.time()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), TextColumn("[yellow]{task.fields[speed]} p/s"), TimeElapsedColumn()) as prog:
        task = prog.add_task("Cracking...", total=None, speed="0")
        with ProcessPoolExecutor(max_workers=optimal_cpu, initializer=attacks.init_worker, initargs=(pdf_path,)) as ex:
            it = gen_func()
            while not found:
                batch = [next(it, None) for _ in range(2000)]
                batch = [b for b in batch if b is not None]
                if not batch: break
                
                for res in ex.map(attacks.check_password_worker, batch):
                    if res: found = res; break
                
                tested += len(batch)
                spd = int((tested - skip_val) / (time.time() - start_t)) if time.time() > start_t else 0
                prog.update(task, advance=len(batch), speed=f"{spd:,}")
                if tested % 10000 == 0: save_session(session_key, tested)
                if found: break

    if found:
        console.print(f"\n[bold green]SUCCESS! Password: {found}[/bold green]")
        utils.save_to_log(os.path.basename(pdf_path), found, "Done")
        if os.path.exists(f"sessions/{session_key}.ptr"): os.remove(f"sessions/{session_key}.ptr")
    else: console.print("\n[red]Not found.[/red]")

if __name__ == "__main__":
    utils.ensure_folders()
    while True:
        try: main_menu(); input("\nPress Enter...")
        except KeyboardInterrupt: sys.exit()