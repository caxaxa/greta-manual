import subprocess

def run_pdflatex(tex_path, output_dir, runs=1):
    for _ in range(runs):
        process = subprocess.Popen(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=output_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        # # print outputs
        # if stdout:
        #     print(stdout)
        # if stderr:
        #     print(stderr)

        # Break the loop if the process had an error
        if process.returncode != 0:
            print(f"Error generating PDF. Return code: {process.returncode}")
            break
    
    if process.returncode == 0:
        print("Compiling successful")
