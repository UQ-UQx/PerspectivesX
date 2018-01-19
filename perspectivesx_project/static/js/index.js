var React = require('react');
var ReactDOM = require('react-dom');

class IconComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {template: props.template, url: " "}
    }

    loadTemplateFromServer() {
        $.ajax({
            url: "/api/Template/" + this.state.template + "/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            type: "GET",
            cache: false,
            success: function (data) {
                this.setState({url: data["icon"]});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadTemplateFromServer();
        // we have all submissions filter so that we keep the one relevant to this activity/perspective
    }

    render() {
        const imgStyle = {
            maxHeight: '100px',
            maxWidth: '100px',
        };
        return (
            <div className="Icon">
                <img src={this.state.url} style={imgStyle}/>
            </div>
        )
    }
}

class ItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {item: props.item}
    }

    deleteItem() {
        $.ajax({
            url: "/api/LearnerSubmissionItem/" + this.state.item.id + "/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            type: "DELETE",
            cache: false,
            beforeSend: function(xhr, settings) {
              console.log("before send run", csrftoken)
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function () {
                $.ajax({
                    url: "/api/LearnerPerspectiveSubmission/" + this.state.item.learner_submission + "/",
                    datatype: 'json',
                    contentType: 'application/json; charset=utf-8',
                    type: "GET",
                    cache: false,
                    success: function (data) {
                        this.props.submissionschanged();
                        /*
                        $.ajax({
                            url: "/perspectivesX/GetSubmissionScore/" + data.id + "/",
                            datatype: 'json',
                            contentType: 'application/json; charset=utf-8',
                            type: "GET",
                            cache: false,
                            success: function (data) {
                                var object = data['0'];
                                alert("Submission updated ! \n" +
                                    " Your new score is: \n" +
                                    "curation grade: " + object['curation_grade'] + "\n" +
                                    "participation grade: " + object['participation_grade'] + "\n" +
                                    "total grade: " + object['total_grade'], 3000);
                            }.bind(this)
                        });
                        */
                    }.bind(this)
                });
            }.bind(this)
        });
    }

    render() {
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor: 'lightgrey',
            marginBottom: '10px'
        };
        var dateString = new Date(this.state.item.created_at);
        dateString = dateString.getDate() + "/" + dateString.getMonth() + "/" + dateString.getFullYear();
        return <li key={this.state.item.id} className="list-group-item">

        <div className="media">
          <div className="media-body">
            <div className="media-meta pull-right action-buttons">
                 <button id='d1' onClick={() => this.deleteItem()} className="btn btn-sm trash"><span className="glyphicon glyphicon-trash"></span></button>
            </div>
            <p className="summary">{this.state.item.item}</p>
            <p className="title">
              Submitted on: {dateString} | Curated by: {this.state.item.number_of_times_curated} users
            </p>

          </div>
        </div>
        </li>
    }

}

/*
<div>Item: {this.state.item.item}</div>
<div>Author:{this.state.item.description.split("from")[1]}</div>
<div>
    <p>
        <button id='d1' onClick={() => this.deleteItem()} className="btn btn-primary btn-sm">delete</button>
    </p>

    <p style={{textAlign: "right"}}>Submitted on: {dateString}<br/>Curated by {this.state.item.number_of_times_curated} users</p>
</div>
*/

class AddItemForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: '',
            submission: [],
            activity: props.activity,
            perspective: props.perspective,
            position: props.position
        }
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    loadSubmissionsFromServer() {
        var cur = this;
        $.ajax({
            url: "/api/LearnerPerspectiveSubmission/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            type: "GET",
            cache: false,
            success: function (data) {
                this.setState({submission: data});
            }.bind(this)
        });
    }

    //This will need to be updated with proper user info !
    componentDidMount() {
        this.loadSubmissionsFromServer();
        /*
        setInterval(() => this.loadSubmissionsFromServer(),
            this.props.pollInterval);
        */

    }

    handleChange(event) {
        this.setState({item: event.target.value})
    }

    handleSubmit(event) {
        var activity = this.state.activity;
        var perspective = this.state.perspective;

        var submissionArray = this.state.submission.filter(function (submission) {
            return (submission.activity == activity.id && submission.selected_perspective == perspective);
        });

        var submission = submissionArray[0];


        event.preventDefault();
        if (submission == undefined) {
            //Create new submission


            $.ajax({
                url: "/api/LearnerPerspectiveSubmission/",
                datatype: 'json',
                contentType: 'application/json; charset=utf-8',
                type: "POST",
                beforeSend: function(xhr, settings) {
                  //console.log("before send run", csrftoken)
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                data: JSON.stringify(
                    {
                        "sharing": "Share with other learners",
                        "selected_perspective": "" + perspective,
                        "created_by": user_id, //username is a global variable
                        "activity": "" + activity.id
                    }),
                success: function (data) {
                    submission = data;
                    $.ajax({
                        url: "/api/LearnerSubmissionItem/",
                        datatype: 'json',
                        contentType: 'application/json; charset=utf-8',
                        crossDomain: true,
                        type: "POST",
                        data: JSON.stringify(
                            {
                                "learner_submission": "" + submission.id,
                                "item": this.state.item,
                                "description": "enter description",
                                "position": this.state.position
                            }),
                        cache: false,
                        beforeSend: function(xhr, settings) {
                          //console.log("before send run", csrftoken)
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        },
                        success: function () {
                            this.props.submissionschanged();
                            this.state.item = "";
                            /*
                            $.ajax({
                                url: "/perspectivesX/GetSubmissionScore/" + submission.id + "/",
                                datatype: 'json',
                                contentType: 'application/json',
                                type: "GET",
                                cache: false,
                                success: function (data) {
                                    var object = data['0'];
                                    alert("Submission updated ! \n" +
                                        " Your new score is: \n" +
                                        "curation grade: " + object['curation_grade'] + "\n" +
                                        "participation grade: " + object['participation_grade'] + "\n" +
                                        "total grade: " + object['total_grade'], 3000);
                                }.bind(this)
                            });
                            */
                        }.bind(this)
                    });
                }.bind(this),
            })
        } else {
            $.ajax({
                url: "/api/LearnerSubmissionItem/",
                datatype: 'json',
                contentType: 'application/json; charset=utf-8',
                crossDomain: true,
                type: "POST",
                beforeSend: function(xhr, settings) {
                  //console.log("before send run", csrftoken)
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                data: JSON.stringify(
                    {
                        "learner_submission": "" + submission.id,
                        "item": this.state.item,
                        "description": "enter description",
                        "position": this.state.position
                    }),
                cache: false,
                success: function () {
                    this.props.submissionschanged();
                    this.state.item = "";
                    /*
                    $.ajax({
                        url: "/perspectivesX/GetSubmissionScore/" + submission.id + "/",
                        datatype: 'json',
                        contentType: 'application/json',
                        type: "GET",
                        cache: false,
                        success: function (data) {
                            var object = data['0'];
                            alert("Submission updated ! \n" +
                                " Your new score is: \n" +
                                "curation grade: " + object['curation_grade'] + "\n" +
                                "participation grade: " + object['participation_grade'] + "\n" +
                                "total grade: " + object['total_grade'], 3000);
                        }.bind(this)
                    });
                    */
                }.bind(this)
            });
        }

    }

    render() {
        return (
            <div className="add-item" style={{float: "right"}}>
                <form onSubmit={this.handleSubmit}>

                <div className="input-group">
                    <input type="text" value={this.state.item} onChange={this.handleChange} className="form-control input-sm chat-input" placeholder="Enter your item here..." />
            	      <span className="input-group-btn">
                      <button type="submit" className="btn btn-primary btn-md">
                        <span className="glyphicon glyphicon-comment"></span> Add Item
                      </button>
                    </span>
                </div>
                </form>
            </div>
        )
    }
}
/*

<label>Add new Item</label>
<input type="text" value={this.state.item} onChange={this.handleChange}/>
<input type="submit" value="Submit" className="btn btn-primary btn-md"/>
*/

class CuratedItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {
            item: props.item,
            inner: {
                "id": -1,
                "description": " ",
                "item": " ",
                "position": 0,
                "created_at": " ",
                "learner_submission": -1
            }
        }

    }

    loadInnerItemFromServer() {
        var cur = this;
        $.ajax({
            url: "/api/LearnerSubmissionItem/" + this.state.item.item + "/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            type: "GET",
            cache: false,
            success: function (data) {
                this.setState({inner: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadInnerItemFromServer();
    }

    deleteItem() {
        $.ajax({
            url: "/api/CuratedItem/" + this.state.item.id + "/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            type: "DELETE",
            cache: false,
            beforeSend: function(xhr, settings) {
              console.log("before send run", csrftoken)
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function () {
                $.ajax({
                    url: "/api/LearnerPerspectiveSubmission/" + this.state.inner.learner_submission + "/",
                    datatype: 'json',
                    contentType: 'application/json; charset=utf-8',
                    type: "GET",
                    cache: false,
                    success: function (data) {
                        $.ajax({
                            url: "/perspectivesX/GetSubmissionScore/" + data.id + "/",
                            datatype: 'json',
                            contentType: 'application/json; charset=utf-8',
                            type: "GET",
                            cache: false,
                            success: function (data) {
                                var object = data['0'];
                                alert("Submission updated ! \n" +
                                    " Your new score is: \n" +
                                    "curation grade: " + object['curation_grade'] + "\n" +
                                    "participation grade: " + object['participation_grade'] + "\n" +
                                    "total grade: " + object['total_grade']);
                            }.bind(this)
                        });
                    }.bind(this)
                });
            }.bind(this)
        });
    }

    render() {
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor: 'lightgrey',
            marginBottom: '10px'
        };
        var dateString = new Date(this.state.inner['created_at']);
        dateString = dateString.getDate() + "/" + dateString.getMonth() + "/" + dateString.getFullYear();
        return <li key={this.state.item.id} className="list-group-item">

        <div className="media">
          <div className="media-body">
            <div className="media-meta pull-right action-buttons">
                 <button id='d1' onClick={() => this.deleteItem()} className="btn btn-sm trash"><span className="glyphicon glyphicon-trash"></span></button>
            </div>
            <p class="summary">{this.state.inner['item']}</p>
            <p class="title">
              Author: {this.state.inner['description'].split("from")[1]} | Submitted on: {dateString} | Curated by: 5 users
            </p>

          </div>
        </div>
        </li>
    }
}

/*

<div>Item: {this.state.inner['item']}</div>
<div>Author:{this.state.inner['description'].split("from")[1]}</div>
<div>
    <p>
        <button id='d1' onClick={() => this.deleteItem()} className="btn btn-primary btn-sm">delete</button>
    </p>
    <p style={{textAlign: "right"}}>Submitted on: {dateString}</p>
</div>


<a href="http://www.jquery2dotnet.com"><span className="glyphicon glyphicon-pencil"></span></a>
<button id='d1' onClick={() => this.deleteItem()} className="btn btn-primary btn-sm">delete</button>
<a href="http://www.jquery2dotnet.com" className="trash"><span className="glyphicon glyphicon-trash"></span></a>
<a href="http://www.jquery2dotnet.com" className="flag"><span className="glyphicon glyphicon-flag"></span></a>
*/

class PerspectiveComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {items: [], curated: [], perspective: props.perspective, activity: props.activity, count: 0};
    }

    loadItemsFromServer() {
        var cur = this;
        //console.log("api url", "/perspectivesX/get_user_submission_items/" + this.state.activity.id + "/" + this.state.perspective + "/" + username +"/");
        $.ajax({
            url: "/perspectivesX/get_user_submission_items/" + this.state.activity.id + "/" + this.state.perspective + "/" + username +"/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function (data) {
                //console.log(data);
                this.setState({items: data});
                this.setState({count: this.state.items.length});
            }.bind(this)
        });

        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_curated_items/" + this.state.activity.id + "/" + this.state.perspective + "/" + username +"/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function (data) {
                this.setState({curated: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadItemsFromServer();
        /*
        setInterval(() => this.loadItemsFromServer(),
            this.props.pollInterval);
        */

    }

    render() {
        const listStyleType = {
            listStyleType: 'none'
        };

        const columnStyle = {
            marginRight: "2px",
            backgroundColor: "white",
            border: "none"
        };
        var itemNodes = this.state.items.map(
            (item) => this.mapItem(item)
        );

        var curatedNodes = this.state.curated.map(
            (curated) => this.mapCuratedItem(curated)
        );

        //if(curatedNodes.length>0 && itemNodes.length>0) {
        if (curatedNodes.length == 0) {
            curatedNodes = <li> No curated items. <a href={"/perspectivesX/display_perspective_items/" + this.state.activity.id + "/" + this.state.perspective + "/"}>Click here to start curating.</a></li>;
        }
        var submissionButtonText = "Edit Submission"
        if (itemNodes.length == 0) {
            itemNodes = <li>No submissions items for this perspective.<br/><br/></li>;
            submissionButtonText = "New Submission"
        }

        var url = "/perspectivesX/submission/" + this.props.activityName.replace(" ", "-").toLowerCase() + "/" + this.state.perspective + "/";

        return (

                    <div className="col-md-6" style={columnStyle}>

                        <div className="panel panel-default">
                            <div className="panel-heading">{this.props.name}</div>
                            <div className="panel-body">
                              <AddItemForm activity={this.state.activity} perspective={this.state.perspective}
                                         position={this.state.count} submissionschanged={this.loadItemsFromServer.bind(this)} pollInterval={this.props.pollInterval}/>
                              <p><strong>Your Submissions:</strong></p>
                              <ul className="list-group" style={listStyleType}>
                                  {itemNodes}
                              </ul>
                              <br/>
                              <p><strong>Curated Submissions:</strong></p>
                              <ul className="list-group" style={listStyleType}>
                                  {curatedNodes}
                              </ul>
                              <br/>
                              <a href={"/perspectivesX/display_perspective_items/" + this.state.activity.id + "/" + this.state.perspective + "/" + resource_link_id +"/"}
                                 className="btn btn-primary btn-block">View other students submissions</a>
                            </div>
                        </div>
                    </div>
        )

    }

    mapCuratedItem(curated){
        return <CuratedItemComponent item={curated} key={curated.id} submissionschanged={this.loadItemsFromServer.bind(this)} pollInterval={this.props.pollInterval}/>
    }
    mapItem(item){
        return <ItemComponent item={item} key={item.id} submissionschanged={this.loadItemsFromServer.bind(this)} pollInterval={this.props.pollInterval}/>
    }
}

/*

<!--<a href={url}
   className="btn btn-primary btn-md" style={{float: "left"}}>{submissionButtonText}
</a>-->
*/

class PerspectiveGridComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {perspectives: [], activity: props.activity};
    }

    loadPerspectivesFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_template_items/" + this.state.activity.id + "/",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function (data) {
                this.setState({perspectives: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadPerspectivesFromServer();
        /*
        setInterval(() => this.loadPerspectivesFromServer(),
            this.props.pollInterval);
            */
    }

    renderPerspectives() {

      var separateElements = [];

      for(var i = 0; i < this.state.perspectives.length; i+=2) {
           var oneRow = [];
           oneRow.push(this.state.perspectives.slice(i, i+2).map(perspective => this.mapPerspectives(perspective)));
           //console.log(oneRow);
           separateElements.push(oneRow.map(itm => {return <div key={i} className="row row-eq-height">{itm}</div>}))
      }

      //console.log(separateElements);
      return separateElements;
    }

    //take care  of no perspective case
    render() {

        const containerStyle = {
            marginLeft: "15px",
            marginRight: "15px"
        };

        if (this.state.perspectives) {
            var perspectiveNodes = this.state.perspectives.map(
                (perspective) => this.mapPerspectives(perspective)
            );
            if (perspectiveNodes.length == 0) {
                perspectiveNodes =
                    <div className="alert alert-warning"><h4>Something went wrong</h4><br/> <p>No perspective for this
                        activity ! </p></div>
            }
            return (

                <div className="row">
                    <div>
                        <h3>{this.state.activity.title}</h3>
                    </div>
                    <div className="container-fluid" style={containerStyle}>

                         {this.renderPerspectives()}

                     </div>

                </div>
            )
        }

    }

    mapPerspectives(perspective) {
        return <PerspectiveComponent activity={this.state.activity} perspective={perspective.id} name={perspective.name}
                                     activityName={this.state.activity.title} key={perspective.id}
                                     pollInterval={this.props.pollInterval}/>;
    }
}


/*
<IconComponent template={this.state.activity.template}/>
*/

class ActivityGridComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {activity: []};

    }

    loadActivitiesFromServer() {
        var cur = this;
        $.ajax({
            url: "/api/Activity/"+this.props.activity_id+"/",
            type: "GET",
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function (data) {
                this.setState({activity: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadActivitiesFromServer();
        /*
        setInterval(() => this.loadActivitiesFromServer(),
            this.props.pollInterval);
        */
    }

    render() {
        if (this.state.activity) {
            const containerStyle = {
                marginLeft: "15px",
                marginRight: "15px"
            };

            /*
            var perspectiveGrids = this.state.activities.map(
                (activity) => this.mapPerspectiveGrid(activity)
            );
            */
            var perspectiveGrids = this.mapPerspectiveGrid(this.state.activity);

            return (

                <div className="container-fluid" style={containerStyle}>
                    {perspectiveGrids}
                </div>
            )
        }

    }

    mapPerspectiveGrid(activity){
        return <PerspectiveGridComponent activity={activity} key={activity.id}
                                                 pollInterval= {this.props.pollInterval}/>
    }
}

console.log('activity_id', activity_id);

ReactDOM.render(<ActivityGridComponent activity_id={activity_id} pollInterval={1000}/>, document.getElementById("container"));
