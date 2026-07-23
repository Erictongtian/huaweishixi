import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('123.60.220.56', username='root', password='Rao13879458112', 
            timeout=15, banner_timeout=30, auth_timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=False)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out[-1500:])
    if err and 'Permission denied' not in err: print('ERR:', err[-500:])
    print(f'exit_code={exit_code}\n')

run("PGPASSWORD='Rao13879458112' psql -U postgres -h localhost -d secondhand_device -c \"\\dt\"")
run("PGPASSWORD='Rao13879458112' psql -U postgres -h localhost -d secondhand_device -c \"\\d users\"")
run("PGPASSWORD='Rao13879458112' psql -U postgres -h localhost -d secondhand_device -c \"\\d email_codes\"")
run('journalctl -u assetmgmt-backend --no-pager -n 20')

ssh.close()