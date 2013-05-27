<?php
/**
 * Controller class for the Searchbox component.
 *
 * this is the main component to execute a query and show result
 */
class PicloaderController extends OntoWiki_Controller_Component {			

		public function picloaderAction(){							
/**	
 * Muss an Endsystem angepasst werden!
 * Server unterstützt nicht alle nötigen Module für upload.
 * 		
		set_time_limit(300);//for setting 
 
		$paths='home\\swp13-wb\\public_html\\OntoWiki\\extensions\\picloader\\images\\'; 
		$filep=$_FILES['userfile']['tmp_name'];
		$ssh_server='pcai042.informatik.uni-leipzig.de';
		$ssh_user_name='swp13-wb';
		$ssh_user_pass='6kf*icad'; //set user data
		$name=$_FILES['userfile']['name'];
 
		$srcFile = $name; //set source file and destination path 
		$dstFile = $paths;

		// Create connection the the remote host
		$conn = ssh2_connect($ssh_server, 22);

		// Create SFTP session
		$sftp = ssh2_sftp($conn);
	
		$sftpStream = @fopen('ssh2.sftp://'.$sftp.$dstFile, 'w'); //creat sftp upstream

		try { //try to connect

			if (!$sftpStream) {
			throw new Exception("Could not open remote file: $dstFile");
			}
    
			$data_to_send = @file_get_contents($srcFile); //upload file
    
			if ($data_to_send === false) {
				throw new Exception("Could not open local file: $srcFile.");
			}
    
			if (@fwrite($sftpStream, $data_to_send) === false) {
				throw new Exception("Could not send data from file: $srcFile.");
			}
    
		fclose($sftpStream); //close connection
                    
		} catch (Exception $e) {
			error_log('Exception:' . $e->getMessage());
			fclose($sftpStream);
		}
*/
}
}
?>
