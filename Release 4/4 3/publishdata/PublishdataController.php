<?php
/**
 * Controller class for the Publishdata component.
 *
 * this is the main component to execute apublishing
 * Developed during a "Software Technik Parktikum 20013" project:
 * http://pcai042.informatik.uni-leipzig.de/~swp13-wb/
 * @author Yves Annanias, Wolf Otto (briefe@wolf-otto.de)
 * @copyright Copyright 2007, strauss esolutions
 * @version 1.0
 * @since 18.05.2013
 */
class PublishdataController extends OntoWiki_Controller_Component {
	/**
	* Method to publish Data to a configered model.
	* 
	* Configuration in the Extension menu in th OntoWiki Instance.
	* Copies a specified model to a ne model with a given label.
	* has the possibility to integrate revers properties specified in a given 
	* vocabulary.
	* Usefull only with disabled Cahce in conf.ini of the working Ontowiki
	* outcomment:
	*  chache.enabele = false
	*  chache.query.enabele = false
	*/
	public function dopublishAction()
		
	{	        		
		// set the main windoe title to 'Publish Data'
		$this->view->placeholder('main.window.title')->set('Publish Data');
		$this->view->urlBase = $this->_config->urlBase;	
		
		// if tab clicked, show plugin-informations
		$doPublish = $this->getParam('doPublish');
		if (!$doPublish)
		{
			$this->view->tabClick = true;			
			return;
		} // else modul-button clicked, publish data an show statistics
			
		 // disable versioning
        $versioning = $this->_erfurt->getVersioning();
        $versioning->enableVersioning(false);

        if ($this->_privateConfig) {
        	
            $this->privConf = $this->_privateConfig->toArray();
 
            /**
            * Method to get the information if a Ressource should be released or not
            * from the config of the Plugin.
            * @param string $status: The status for which zou want to know if it should be released.
           	* @return true if it is ready to release, false else.
            */
			function doRelease($status) {
				return(
					($this->privConf->criteria->publishOnlySigned) ? 
						($status == $this->privConf->criteria->release) :
					($status != $this->privConf->criteria->doNotRelease && 
						$status != $this->privConf->criteria->neverRelease)
						
					) ;
			}
			
//			beginning of a message which is displayed in main window
			$this->message = '';
			// Get base information
            $efApp = Erfurt_App::getInstance();
			$efStore = $efApp->getStore();
			$availableModels = $efStore->getAvailableModels();
			
			
//			Help Methods
//			------------
			/**
			* Method to Transform all modelUri parts in an SPARQL Query answer
			* @param $oldUris: The array which is returned from SPARQL Query
			* @param string $oldmodel: A model like http://yourmodel.com/ which should be replaced
			* @param string $newmodel: A model like http://yournewmodel.com/ is the one you want
			* @return The whole set with replaced modelPart in URI
			*/
			function replaceUri($oldUris, $oldmodel, $newModel) 
			{	
				$newUris = array();
				foreach ($oldUris as $oneKey => $oneUri) 
				{
					$newUris[$oneKey] = str_replace($oldmodel, $newModel, $oneUri);
//					$this->message .= $oneUri . '<br>';
				}
				return $newUris;
			}
			
//			ModelManagment
//			--------------

//			Askes if Model which should be published exists,
			if (array_key_exists($this->privConf['models']['workingModel'], $availableModels)) 
			{
		    	$this->modelToPublish  = $efStore->getModel( $this->privConf['models']['workingModel'] );
			}
			else 
			{
				$this->_owApp->appendMessage(
               			new OntoWiki_Message('Model you want to publish do not exist.', OntoWiki_Message::WARNING)
            			);
            	return;
			}
//			Gets Targetmodel 
//			$this->modelTarget  = $efStore->getModelorCreate( $this->privConf['models']['targetModel'] );
//			deletes targetmodel if it exists
			if ($efStore->isModelAvailable($this->privConf['models']['targetModel']))  
			{
		    	$efStore->deleteModel($this->privConf['models']['targetModel']);
			}	
//			creates and choose new model			
			$this->modelTarget = $efStore->getNewModel($this->privConf['models']['targetModel']);			
//			modelUri for link in dopublish.phtml			
			$this->view->targetModel = $this->modelTarget;
						
//			Adds model for vocabulary if it exists
			if ($efStore->isModelAvailable($this->privConf['models']['vocabulary']))
			{
			    $this->modelVocabulary = $efStore->getModel( $this->privConf['models']['vocabulary'] );
			}
			else
			{
				$this->_owApp->appendMessage(
               			new OntoWiki_Message('Model of your Vocabulary does not exist.', OntoWiki_Message::INFO)
            			);            	
			}
			
//			Do Insertion
//			------------

//			Copies the given model with specified configuration into exportmodel
			$this->askAndInsert();

//			Output to MainWindow
//			--------------------
			$this->view->ausgabe = array(array(""));
			$this->view->query = "";
				
			$this->view->message =   $this->messageStats;

        }
//    	enable Versioning
    	$versioning->enableVersioning(true);    	    	
        
	}
	
	
	private function askAndInsert()
	{
//			Get Ressources to Publish
//			-------------------------
//			-------------------------

//		Get Literal Ressources
//		----------------------
		$registeredLang = $this->privConf['Language']['langOfLiterals'];
//		@todo Ask if there is any Array in the config
		$deleteLangAnnotation = $this->privConf['Language']['noLangAnn']; 
		if ($deleteLangAnnotation)
		{
			$registeredLang = array("");
		}
		if (! (in_array("",$registeredLang)))
		{
			array_push($registeredLang, "");
		}
		//			set Timer
		$begin = microtime(true);
	
		$allLabelRes = array();		
		foreach ( $registeredLang as $langLabel){
			$queryBaseRes = new Erfurt_Sparql_SimpleQuery();
          	$queryBaseRes	->setProloguePart('SELECT ?subj ?prop ?obj ?lang  ')
				->setWherePart('WHERE {' .
							'?subj  ?prop ?obj . ' . 
							' FILTER  ( isLITERAL(?obj)) ' .
							($deleteLangAnnotation ? "":
							' FILTER  ( LANG(?obj) = "' . $langLabel .'")' )  .
							' FILTER regex (?subj, "' . (string) $this->modelToPublish . '","i") ' .  					
						'} ') ;
			$resultBaseRes = $this->modelToPublish->sparqlQuery($queryBaseRes);
//			Adds the lang label to an Literal 
//			It is not possible to get lang label via SPARQL in Erfurt  because BIND (SPARQL 1.1) is not supported
			foreach ($resultBaseRes as &$oneResult) {
				$oneResult['lang'] = $langLabel;
//				$this->message .= $oneResult['lang'];
			}
			unset($oneResult);
			$allLabelRes = array_merge($allLabelRes, $resultBaseRes);
		}
		$executionTime = (microtime(true) - $begin);
		$this->messageStats['SPARQL Abfrage Literale'] = number_format($executionTime, 2, ",", "") . " s";	



//		Get URI Ressources
//		----------------------
		$begin = microtime(true);
		$queryBaseRes = new Erfurt_Sparql_SimpleQuery();
        $queryBaseRes	->setProloguePart('SELECT ?subj ?prop ?obj')
				->setWherePart('WHERE {' .
							'?subj  ?prop ?obj . ' . 
							' FILTER  ( isUri(?obj)). ' .
							' FILTER regex (?subj, "' . (string) $this->modelToPublish . '","i") ' .  					
						'} ') ;
		$resultBaseRes = $this->modelToPublish->sparqlQuery($queryBaseRes);
		$resultBaseRes = array_merge($allLabelRes, $resultBaseRes);

		$executionTime = (microtime(true) - $begin);
		$this->messageStats['SPARQL Abfrage URIs'] = number_format($executionTime, 2, ",", "") . " s";


//		Delete all Ressources, which should not be added
//		-----------------------------------------------
//		-----------------------------------------------		

//		Get StatusLists of Ressources and deletes singened Ressources
//		-------------------------------------------------------------
		$begin = microtime(true);
		$readyToRel = $this->privConf['criteria']['release'];
		$doNotRel = $this->privConf['criteria']['doNotRelease'];
		$neverRel = $this->privConf['criteria']['neverRelease'];
		
		$publishOnlySingned = $this->privConf['criteria']['publishOnlySingned'];
		$listOfResToDelete = array();// list of all Ressources that should not be added in any Relation
		$listOfResRelease = array();// list of all Ressources that should not be added in any Relation		

		$newresultBaseRes = array();		
		foreach ($resultBaseRes as $triple)
		{

			if (($triple['obj'] === $doNotRel) || ($triple['obj'] === $neverRel))
			{
				array_push($listOfResToDelete, $triple['subj']);
//				$this->message .= "<br>NICHT VEROEFFENTLICHEN: ". $triple['subj']. '  '.$triple['prop'].'  '.$triple['obj']. '<br>';
			}
			else
			{
				if ($triple['obj'] === $readyToRel)
				{
					array_push($listOfResRelease, $triple['subj']);
				}
				array_push($newresultBaseRes, $triple);
			}
		}
		$resultBaseRes = $newresultBaseRes;		
		unset($newresultBaseRes);
		
//		Delete all Ressources not to be published
//		-----------------------------------------
		$newresultBaseRes = array();
		foreach ($resultBaseRes as $triple)
		{
//			Delete all Ressources and Relation singned not to publish
			if (! (in_array($triple['obj'], $listOfResToDelete )) && ! (in_array($triple['subj'], $listOfResToDelete ))) 
			{
				if ($publishOnlySingned)
				{	
					//subj is ready
					$subjReady = in_array($triple['subj'], $listOfResRelease );
					//obj is ready or a literal
					$objReady = (in_array($triple['obj'], $listOfResRelease) || array_key_exists('lang', $triple));
					if ($subjReady && $objReady)
					{
						array_push($newresultBaseRes, $triple);	
					} 	
					//else the triple should not be published
				}
				else
				{
					array_push($newresultBaseRes, $triple);
				}
			}
//			else
//			{						{
//				$this->message .= "<br>Es wurde ein Objekt Tripel geloescht von Objekt: ". $triple['subj']. '  '.$triple['prop'].'  '.$triple['obj']. '<br>';
//			}
			

		}
		$resultBaseRes = $newresultBaseRes;		
		unset($newresultBaseRes);
		
//		Insert relations with inverse Properties 
//		------------------------
		if ($this->privConf['criteria']['publishInversRelations'])
		{
//			Generates invers Property Array
			$this->getInvPropArray();
			$inversTripleCounter = 0;	
			$newresultBaseRes = array();
			foreach ($resultBaseRes as $triple)
			{
				if (array_key_exists($triple['prop'], $this->invPropArray) && !(array_key_exists('lang', $triple)))
				{
//					$this->message .= "<br>FUEGT INVERS HINZU: ". $triple['subj']. '  '.$triple['prop'].'  '.$triple['obj']. '<br>'.
										$triple['obj']. '  '.$this->invPropArray[$triple['prop']] .'  '.$triple['subj'];
					$inversTriple['subj'] = $triple['obj'];
					$inversTriple['prop'] = $this->invPropArray[$triple['prop']];
					$inversTriple['obj'] = $triple['subj'];
					array_push($newresultBaseRes, $triple);
					if (! (in_array($inversTriple, $newresultBaseRes)))
					{
						$inversTripleCounter += 1;
						array_push($newresultBaseRes, $inversTriple);
					}
				}
				else
				{
					array_push($newresultBaseRes, $triple);
				}
			}
			$this->messageStats['Inverse Relationen eingefuegt'] = $inversTripleCounter ;
			$resultBaseRes = $newresultBaseRes;		
		}
		
		$executionTime = (microtime(true) - $begin);

		$this->messageStats['Bearbeitung der Daten'] = number_format($executionTime, 2, ",", "") . " s";

		
		
//		$this->message .= '<br>' . $queryBaseRes .'<br>';
//		$resultBaseRes = $this->modelToPublish->sparqlQuery($queryBaseRes);
//		if (!$resultBaseRes) ;
//		{
//			return false;
//		}
				
		
//
		
//			Insert Ressources in modelTarget
//			--------------------------------
		$begin = microtime(true);
		$this->messageStats['Einzufuegende Tripel'] = count($resultBaseRes) ;
		$tripleCounter = 0;	
		foreach ($resultBaseRes as $triple) 
		{
			$tripleCounter += 1;	
			
//			Replace all old Model uri with new model uri
			$triple = replaceUri($triple, (string)$this->modelToPublish, (string)$this->modelTarget);
			$subj = $triple['subj'];
			$prop = $triple['prop'];
			$obj = $triple['obj'];

			if (array_key_exists('lang',$triple) )
			{
//				Insert Literal keys
				$lang = $triple['lang'];
				if ($subj !== (string)$this->modelTarget) //The label from the old model is not copied
				{
					$this->modelTarget->addStatement($subj, $prop, array('value' => $obj, 'type' => 'literal', 'lang' => $lang));
				}
			}
			else
			{
//				Insert URIs
				$this->modelTarget->addStatement($subj, $prop, array('value' => $obj, 'type' => 'uri'));
			}

		}
//		Iserts new Modelname in modelTarget
		$this->modelTarget->addStatement((string)$this->modelTarget, 
			'http://www.w3.org/2000/01/rdf-schema#label' , 
			array('value' => $this->privConf['models']['targetMLabel'], 'type' => 'literal'));
//		$this->message .= '</table>';
		$executionTime = (microtime(true) - $begin);
		$this->messageStats['Einfuegen der Daten in Ziel Model'] = number_format($executionTime, 2, ",", "") . " s";
		
		return true;
	}
	
	/**
	* Mathod to generate a array() like this [ 'property' => 'inverseProperty', ...]
	* and stores it in $this->invPropArray
	*/
	private function getInvPropArray()
	{	
		if (array_key_exists('modelVocabulary', $this))
		{
			$begin = microtime(true);
	    	$queryBaseRes = new Erfurt_Sparql_SimpleQuery();
	    	$queryBaseRes	->setProloguePart('SELECT ?prop ?revProp')
						->setWherePart('WHERE {' .
						 '?prop <http://www.w3.org/2002/07/owl#inverseOf> ?revProp . ' .
						' FILTER regex (?prop, "' . (string) $this->modelVocabulary . '","i") ' .  					
					'} ') ;
			$inverseProperties = $this->modelVocabulary->sparqlQuery($queryBaseRes);
			$invPropArray = array();
			foreach($inverseProperties as $invPropCombi ) 
			{
				$invPropArray[$invPropCombi['prop']] = $invPropCombi['revProp'];
//				$this->message .= '<br>' . $invPropCombi['prop'] . ' vs. ' . $invPropCombi['revProp'];
			}
			unset($inverseProperties);
			$this->invPropArray = $invPropArray;
			$executionTime = (microtime(true) - $begin);
			$this->messageStats['Abfragen der Inversen Properties'] = number_format($executionTime, 2, ",", "") . " s";
		}
		else
		{
			$this->invPropArray = array();
			$this->_owApp->appendMessage(
               			new OntoWiki_Message('Select an existing Model to get Invers Relations.', OntoWiki_Message::WARNING)
            			);
		}
	}
}



//	private function createTree($triples)
//	{
//		$tree3 = array();
//		foreach($triples as $triple)
//		{
//			$tree3[$triple['subj']] = array();
//		}
//
//		foreach($triples as $triple)
//		{
//			array_push($tree3[$triple['subj']], array($triple['prop'] => $triple['obj']));
//		}
//		$fullTree = $tree3;
//		$knownRes = array()
//		foreach($fullTree as $subj => $propObjs)
//		{
//			array_push($knownRes, $subj);
//			set($nextPartArray, $knownRes) = $this->recuTreeBuild($propObjs, $tree3, $knownRes) 
//			$propObjs = $nextPartArray
//		} 
//	}
//	private function recuTreeBuild($propObjs, $tree3, $knownRes)
//		{
//			$partArray = array();
//			foreach($propObjs as $prop => $obj)
//			{
//				if ($obj in $knownRes)
//				{
//					array_push($partArray, array($prop => $obj);
//				}
//				else
//				{
//					set($nextPartArray, $knownRes) = $this->recuTreeBuild($tree3[$obj], $tree3, $base, $knownRes)
//					array_push($partArray, array($prop => array($obj => $nextPartArray)));
//				}
//			}
//				
//			return $partArray, $knownRes;
//		} 
//
			

