# Base image for Python with CUDA support
FROM --platform=linux/x86_64 nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Miniconda
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda init bash && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Update PATH environment variable
ENV PATH="/opt/conda/bin:$PATH"

# Set up working directory
WORKDIR /app

# Copy environment.yml file into the container
COPY environment.yml /app/environment.yml

# Install the conda environment defined in the YAML file
RUN conda env create -f /app/environment.yml

# Activate the environment
SHELL ["conda", "run", "-n", "protectio", "/bin/bash", "-c"]

# Install any necessary packages for CUDA compatibility in your Python environment
# For example, to install pytorch with CUDA support
RUN conda install -n protectio -c pytorch pytorch cudatoolkit=11.8

# Copy necessary scripts and data into the container
COPY stand_alone_prediction.sh /app/
COPY entrypoint.sh /app/entrypoint.sh
COPY pred_motif_acw.py /app/
COPY pred_motif_wcw.py /app/
COPY pred_dnabert2_cbe_sv1.py /app/
COPY pred_dnabert2_cbe_snv1.py /app/
COPY DNABERT-2-CBE_Suzuki_v1/ /app/DNABERT-2-CBE_Suzuki_v1/
COPY DNABERT-2-CBE_Suzuki_Nakamae_v1/ /app/DNABERT-2-CBE_Suzuki_Nakamae_v1/
COPY example/ENST00000288774_target_with_header.fasta /app/example/

# Ensure the bash script is executable
RUN chmod +x /app/stand_alone_prediction.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint to activate conda environment and run commands
ENTRYPOINT ["/app/entrypoint.sh"]

# Define the default command to execute when running the container
CMD ["bash"]
