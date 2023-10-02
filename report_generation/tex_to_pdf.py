import subprocess

def run_pdflatex(tex_path, output_dir):
    process = subprocess.Popen(["pdflatex", tex_path], cwd=output_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        error_output = process.stderr.readline()
        
        if output:
            print(output.strip())
        if error_output:
            print(error_output.strip())

        # Break the loop if the process is done
        return_code = process.poll()
        if return_code is not None:
            print(f"Return code: {return_code}")
            break

    if return_code == 0:
        print("PDF generated successfully!")
    else:
        print("Error generating PDF.")
