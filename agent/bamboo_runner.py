import subprocess
from typing import Optional

class BambuRunner:
    """
    A utility class to interface with the Bambu High-Level Synthesis (HLS) tool.
    Handles hardware synthesis and simulation via subprocess calls.
    """

    @staticmethod
    def run_bambu_synthesis(
        c_file_name: str, 
        top_fname: str, 
        generate_tb: str, 
        working_directory: str
    ) -> Optional[str]:
        """
        Executes the Bambu synthesis process for a given C file.

        Args:
            c_file_name: The source C file to synthesize.
            top_fname: The name of the top-level function.
            generate_tb: Path or flag for testbench generation.
            working_directory: The directory where the command should execute.

        Returns:
            An error report string if synthesis fails, otherwise None.
        """
        command = [
          "bambu",
          c_file_name,
          f"--top-fname={top_fname}",
          "--device-name=xc7z020-1clg484-VVD",
          "--clock-period=5",
          f"--generate-tb={generate_tb}",
          "-v4",
          "-I../../common"
        ]
        try:
            # We still capture output, but we don't print it unless an exception occurs
            subprocess.run(command,cwd=working_directory,
                          capture_output=True, text=True, check=True)
            return None

        except subprocess.CalledProcessError as e:
            # Construct the error report
            error_report = f"Standard Error:\n{e.stderr}\nStandard Output:\n{e.stdout}"
            # Return the error for LangGraph/LLM processing
            return error_report

    @staticmethod
    def run_bambu_simulation(
        tb_file: str, 
        top_fname: str, 
        working_dir: str, 
        source_file: str = "aes.c"
    ) -> Optional[str]:
        """
        Runs a simulation of the synthesized hardware using Bambu.

        Args:
            tb_file: Path to the testbench file.
            top_fname: The name of the top-level function.
            working_dir: Execution directory.
            source_file: The source C file used for simulation.

        Returns:
            The full simulation output string on success, or None on failure.
        """
        command = [
            "bambu",
            "--generate-interface=INFER",
            f"--generate-tb={tb_file}",
            source_file,
            f"--top-fname={top_fname}",
            "--simulate",
            "-v1",
            "-I../../common"
        ]

        try:
            result = subprocess.run(
                command,
                cwd=working_dir,
                check=True,
                text=True,
                stdout=subprocess.PIPE,     # Capture success logs
                stderr=subprocess.STDOUT    # Merge stderr into stdout for unified logging
            )
            
            print(result.stdout)
            return result.stdout

        except subprocess.CalledProcessError as e:
            print(f"\nCommand failed with exit code {e.returncode}")
            print(f"Error Output:\n{e.output}")
            return None
            
        except FileNotFoundError:
            print(
                f"\nError: 'bambu' executable not found in PATH or "
                f"directory '{working_dir}' does not exist."
            )
            return None