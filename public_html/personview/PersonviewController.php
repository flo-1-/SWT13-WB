<?php
/**
 * Controller class for the Searchbox component.
 *
 * this is the main component to execute a query and show result
 */
class PersonviewController extends OntoWiki_Controller_Component {			
			
		/**
		 * main search Action
		 * - see Helper class and Module class
		 */	
		public function personviewAction(){
		 $commentcount = 1;
		 $string = "";
		 $resource   = $this->_owApp->selectedResource;
		 $query = new Erfurt_Sparql_SimpleQuery(); 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMainName> ?MNRes . '.
		 '?MNRes <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 'FILTER (langMatches(lang(?label), "de"))'.
		 '}');
		 $this->model = $this->_owApp->selectedModel;
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"];
		 }
		 $this->view->MNamestring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMainName> ?MNRes . '.
		 '?MNRes <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 'FILTER (langMatches(lang(?label), "ru")||(langMatches(lang(?label), "dr"))'.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] . ' / ';
		}
		$query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasAlternativeName> ?ANRes . '.
		 '?ANRes <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 'FILTER (langMatches(lang(?label), "ru")||(langMatches(lang(?label), "dr"))'.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] . ' / ';
		}
		$query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasAlternativeName> ?ANRes . '.
		 '?ANRes <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 'FILTER (langMatches(lang(?label), "de")||(langMatches(lang(?label), "rd"))'.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] . ' / ';
		}
		 $this->view->ANamestring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?Alabel ?Mlabel ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasAlternativeName> ?ANRes . '.
		 '?ANRes <http://drw-model.saw-leipzig.de/hasNameVariation> ?AVRes . '.
		 '?AVRes <http://www.w3.org/2000/01/rdf-schema#label> ?Alabel . '.
		 '<'.$resource.'> <http://drw-model.saw-leipzig.de/hasMainName> ?MNRes . '.
		 '?MNRes <http://drw-model.saw-leipzig.de/hasNameVariation> ?MVRes . '.
		 '?MVRes <http://www.w3.org/2000/01/rdf-schema#label> ?Mlabel . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["Mlabel"] . ' / ';
		}
		foreach($queryResult as $item){
			 $string .= $item["Alabel"] . ' / ';
		}
		 $this->view->VNamestring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?timelabel ?placelabel ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/wasBornOn> ?timeO . '.
		 '?timeO <http://www.w3.org/2000/01/rdf-schema#label> ?timelabel . '.
		 '<'.$resource.'> <http://drw-model.saw-leipzig.de/wasBornIn> ?placeO . '.
		 '?placeO <http://www.w3.org/2000/01/rdf-schema#label> ?placelabel . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 $string = '*';
		 foreach($queryResult as $item){
			 $string .= $item["timelabel"]. " " . " " . $item["placelabel"];
		 }
		 $this->view->Bstring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?timelabel ?placelabel ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/diedOn> ?timeO . '.
		 '?timeO <http://www.w3.org/2000/01/rdf-schema#label> ?timelabel . '.
		 '<'.$resource.'> <http://drw-model.saw-leipzig.de/diedIn> ?placeO . '.
		 '?placeO <http://www.w3.org/2000/01/rdf-schema#label> ?placelabel . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 $Dstring = '†';
		 foreach($queryResult as $item){
			 $string .= $item["timelabel"]. " " . " " . $item["placelabel"];
		 }
		 $this->view->Dstring = $string;
		 $string = "";    
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasGeneralLabor> ?labor . '.
		 '?labor <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"].", ";
		 }
		 $this->view->Lstring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasFatherComment> ?FatherComment . '.
		 '?FatherComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 } 
		 }
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/fatherIs> ?father . '.
		 '?father <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] ;
		 }
		 $this->view->Fatherstring = $string;
		 $string = "";    
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMotherComment> ?MotherComment . '.
		 '?MotherComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/motherIs> ?mother . '.
		 '?mother <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] ;
		 }
		 $this->view->Motherstring = $string;
		 $string = ""; 
		 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMarriagePartnerComment> ?MPComment . '.
		 '?MPComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }
		 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMarriagePartner> ?E . '.
		 '?E <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] ;
		 }
		 $this->view->MPstring = $string;
		 $string = ""; 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasSiblingsComment> ?SComment . '.
		 '?SComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }		 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasSiblings> ?S . '.
		 '?S <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] ;
		 }
		 $this->view->Sibstring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasDescendantsComment> ?DComment . '.
		 '?DComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }
		 		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasDescendant> ?D . '.
		 '?D <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= $item["label"] ;
		 }
		 $this->view->Descstring = $string;
		 $string = "";
						

		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasEducationComment> ?EComment . '.
		 '?EComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }
						
		 $query->setProloguePart('SELECT ?Beginlabel ?Endlabel ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasEducation> ?education . '.
		 '?education <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '?education <http://drw-model.saw-leipzig.de/began> ?beginO  . '.
		 '?beginO <http://www.w3.org/2000/01/rdf-schema#label> ?Beginlabel .'.
		 '?education <http://drw-model.saw-leipzig.de/ended> ?endO  . '.
		 '?endO <http://www.w3.org/2000/01/rdf-schema#label> ?Endlabel .'.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= "•". $item["Beginlabel"]; 
			 if ($item["Endlabel"] != ""){
				 $string .= "-". $item["Endlabel"] . " ";
			 }
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->Estring = $string;
		 $string = "";    
		
		  $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasStationsOfLifeComment> ?SOLComment . '.
		 '?SOLComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }
		 		
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasStationOfLife> ?SOL . '.
		 '?SOL <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '?SOL <http://drw-model.saw-leipzig.de/began> ?beginO  . '.
		 '?beginO <http://www.w3.org/2000/01/rdf-schema#label> ?Beginlabel .'.
		 '?SOL <http://drw-model.saw-leipzig.de/ended> ?endO  . '.
		 '?endO <http://www.w3.org/2000/01/rdf-schema#label> ?Endlabel .'.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= "•" . $item["Beginlabel"]; 
			 if ($item["Endlabel"] != ""){
				 $string .= "-". $item["Endlabel"] . " ";
			 } 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->SOLstring = $string;
		 $string = "";
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasHonoursAndAwardsComment> ?HAAComment . '.
		 '?HAAComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 $comm = "";
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }		 
		 
		 $this->view->EuA = "";
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasHonoursAndAwards> ?HAA . '.
		 '?HAA <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $this->view->EuA = "Ehrungen und Auszeichnungen";
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->HAAstring = $string;
		 $string = "";
		 
		  $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasWL> ?WL . '.
		 '?WL <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){
			 $string .= "•"; 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->WLstring = $string;
		 $string = "";    	    					
			
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMembershipComment> ?MComment . '.
		 '?MComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }

		  $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasMG> ?MG . '.
		 '?MG <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->MGstring = $string;
		 $string = "";  
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasW> ?W . '.
		 '?W <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->Wstring = $string;
		 $string = "";  
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasQ> ?S . '.
		 '?S <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->Sstring = $string;
		 $string = ""; 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasSLComment> ?SLComment . '.
		 '?SLComment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 if ((is_array($queryResult) || isset ($queryResult[0]) || is_array($queryResult[0]))){
			 foreach($queryResult as $item){
				$string .= $item["label"] ;
				$string .= "<br>"; 
			 }
		 }

		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasSL> ?SL . '.
		 '?SL <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->SLstring = $string;
		 $string = "";

		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasP> ?P . '.
		 '?P <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->Pstring = $string;
		 $string = ""; 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasGPV> ?GPV . '.
		 '?GPV <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->GPVstring = $string;
		 $string = ""; 
		 
		 $query->setProloguePart('SELECT ?image ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://xmlns.com/foaf/0.1/img> ?image . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["image"] ;
		 }
		 $this->view->Bildstring = $string;
		 $string = ""; 
		 
		 
		 $query->setProloguePart('SELECT ?ID ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasID> ?ID . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 foreach($queryResult as $item){ 
			 $string .= $item["ID"] ; 
		 }
		 $this->view->IDstring = $string;
		 $string = ""; 
		 
		 $query->setProloguePart('SELECT ?label ')->setWherePart(
		 'WHERE{ <'.$resource.'> <http://drw-model.saw-leipzig.de/hasComment> ?Comment . '.
		 '?Comment <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.
		 '}');
		 $queryResult = $this->model->sparqlQuery($query);
		 $comm = "";
		 foreach($queryResult as $item){
			 $string .= "- ";
			 $string .= $item["label"] ;
			 $string .= "<br>"; 
		 }
		 $this->view->Cstring = $string;
		 $string = ""; 
		}	
}
