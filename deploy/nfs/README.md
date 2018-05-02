# NFS
We create an AWS EFS and mount it with NFS to use as the users' home directories.

On the AMI we used, `nfs-utils` is already installed.
Otherwise, `sudo yum install nfs-utils` to install an NFS client.

We need to create a security group that opens up TCP 2409, which is used by NFS clients.

[EFS](http://docs.aws.amazon.com/efs/latest/ug/mount-fs-auto-mount-onreboot.html) gives us the mount command to use and also an entry for `/etc/fstab`.
Put the following in `/etc/fstab`:
```
mount-target-DNS:/ efs-mount-point nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0
```
Note that it appears that we (currently) can't just do a `sudo mount`, as Docker needs to have the mount info in `/etc/fstab` to actually mount the volume.
Note that you'll also need to restart the docker service (`sudo service docker restart`) if you add the mount after installing/starting docker.
See [here](https://forums.docker.com/t/docker-fails-to-mount-v-volume-from-nfs-mounted-directory/582/19) for a thread on the topic.

For us, EFS gives a mount-target-DNS that's something like `fs-XXXXXXX.efs.REGION.amazonaws.com`, so you'll add that and change the efs-mount-point to wherever you want to mount the EFS to the host machine.
For us, we're going to mount it to `/mnt/nfs/home` and then bind that volume to `/home` in the Docker Jupyter notebook server containers.

JMF 1 May 2018: I needed to add the appropriate security groups in the "file system access" page.

```bash
sudo mkdir -p /mnt/nfs/home
```

Now reboot the machine, and then do a `sudo mount /mnt/nfs/home` once logged back in.

It looks like docker is setting the owner to UIDs instead of usernames, which is less than ideal.
We must ensure that all USER/UID pairs are the same across all nodes.
Then how to ensure that  docker isn't changing the owner names to UIDs?  Or at least make sure the UIDs are the pre-assigned system UIDs.
JMF 14 May 2017: changed the `useradd` command in the notebook container `systemuser.sh`

It looks like we don't need to have the users on the worker nodes.  Potentially just the JHub machine.
