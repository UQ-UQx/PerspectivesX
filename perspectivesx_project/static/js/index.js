var React = require('react');
var ReactDOM = require('react-dom');

class ItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {item: props.item}

    }

    deleteItem(){
        $.ajax({
            url: "/api/LearnerSubmissionItem/" + this.state.item.id+"/",
            datatype: 'json',
            type: "DELETE",
            cache: false,
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
        return <li key={this.state.item.id} style={liStyle}>
            <div>Item: {this.state.item.item}</div>
            <div>Author:{this.state.item.description.split("from")[1]}</div>
            <div>
                <p><button id = 'd1' onClick = {() => this.deleteItem()} className = "btn btn-primary btn-sm" >delete</button></p>
                <p style={{textAlign: "right"}}>Submitted on: {dateString}</p>
            </div>
        </li>
    }

}

class AddItemForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {item: '',submission: [], activity: props.activity, perspective: props.perspective, position: props.position}
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    loadSubmissionsFromServer(){
        var cur = this;
          $.ajax({
            url: "/api/LearnerPerspectiveSubmission/",
            datatype: 'json',
            type:"GET",
            cache: false,
            success: function (data) {
                this.setState({submission: data});
            }.bind(this)
        });
    }

    //This will need to be updated with proper user info !
    componentDidMount() {
        this.loadSubmissionsFromServer();
        // we have all submissions filter so that we keep the one relevant to this activity/perspective

    }

    handleChange(event) {
        this.setState({item: event.target.value})
    }

    handleSubmit(event) {
        var activity = this.state.activity;
        var perspective = this.state.perspective;
        var submissionArray = this.state.submission.filter(function(submission) {
            return (submission.activity == activity && submission.selected_perspective == perspective);
        });
        var submission = submissionArray[0]


        event.preventDefault();
        $.ajax({
            url: "/api/LearnerSubmissionItem/",
            datatype: 'json',
            contentType:'application/json; charset=utf-8',
            crossDomain: true,
            type: "POST",
            data: JSON.stringify(
                {
                "learner_submission":""+submission.id,
                "item":this.state.item,
                "description": "asdadsad",
                "position":this.state.position
                }),
            cache: false,


        });
        // window.location.href = "add_submission_item/" + this.state.activity + "/" + this.state.perspective +
        //     "/" + this.state.position + "/" + this.state.item + "/";

    }

    render() {
        return (
            <div className="add-item" style={{float: "right"}}>
                <form onSubmit={this.handleSubmit}>
                    <label>Add new Item</label>
                    <input type="text" value={this.state.item} onChange={this.handleChange}/>
                    <input type="submit" value="Submit" className="btn btn-primary btn-md"/>
                </form>
            </div>
        )
    }
}

class CuratedItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {item: props.item}

    }

    render() {
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor: 'lightgrey',
            marginBottom: '10px'
        };
        var dateString = new Date(this.state.item.created_at);
        dateString = dateString.getDate() + "/" + dateString.getMonth() + "/" + dateString.getFullYear();
        return <li key={this.state.item.id} style={liStyle}>
            <div>Item: {this.state.item.item}</div>
            <div>Author:{this.state.item.description.split("from")[1]}</div>
            <div>
                <p><a href={"/perspectivesX/delete_curated_item/" + this.state.item.id + "/"}>delete</a></p>
                <p style={{textAlign: "right"}}>Submitted on: {dateString}</p>
            </div>
        </li>
    }

}


class PerspectiveComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {items: [], curated: [], perspective: props.perspective, activity: props.activity};
    }

    loadItemsFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_submission_items/" + this.state.activity + "/" + this.state.perspective + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({items: data});
            }.bind(this)
        });
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_curated_items/" + this.state.activity + "/" + this.state.perspective + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({curated: data});
            }.bind(this)
        });
    }


    componentDidMount() {
        this.loadItemsFromServer();
        setInterval(() => this.loadItemsFromServer(),
            this.props.pollInterval);

    }

    render() {
        const listStyleType = {
            listStyleType: 'none'
        };
        const containerStyle = {
            marginLeft: "15px",
            marginRight: "15px"
        };

        const columnStyle = {
            marginRight: "10px",
        };
        var itemNodes = this.state.items.map(function (item) {
            return <ItemComponent item={item} key={item.id}/>

        });



        var curatedNodes = this.state.curated.map(function (curated) {
            return <CuratedItemComponent item={curated} key={curated.id}/>
        })
        //if(curatedNodes.length>0 && itemNodes.length>0) {
        if (curatedNodes.length == 0) {
            curatedNodes = <li> No curated items. <br/><a
                href={"/perspectivesX/display_perspective_items/" + this.state.activity + "/" + this.state.perspective + "/"}
                className="btn btn-primary btn-md">Start Curating</a></li>;
        }
        var submissionButtonText = "Edit Submission"
        var count = 0;
        if (itemNodes.length == 0) {
            itemNodes = <li>No submissions items for this perspective.<br/><br/></li>;
            submissionButtonText = "New Submission"
        }else{
            var count = itemNodes.length;
        }
        if(this.state.activity == 7){
            console.log(count);
        }
        var url = "/perspectivesX/submission/" + this.props.activityName.replace(" ", "-").toLowerCase() + "/" + this.state.perspective + "/";

        return (
            <div className="container-fluid" style={containerStyle}>
                <div className="row row-eq-height">
                    <div className="col-md-6" style={columnStyle}>
                        <div className="well">
                            <p>Submitted for {this.props.name} :</p>
                            <ul style={listStyleType}>
                                {itemNodes}
                                <a href={url}
                                   className="btn btn-primary btn-md" style={{float: "left"}}>{submissionButtonText}
                                </a>
                                <AddItemForm activity={this.state.activity} perspective={this.state.perspective}
                                             position= {count}/>
                            </ul>
                            <br/><br/>
                            <a href={"/perspectivesX/display_perspective_items/" + this.state.activity + "/" + this.state.perspective + "/"}
                               className="btn btn-primary btn-md">View all</a>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="well">
                            <p>Curated for {this.props.name} :</p>
                            <ul style={listStyleType}>
                                {curatedNodes}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        )

    }
}


class PerspectiveGridComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {perspectives: []};

    }

    loadPerspectivesFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_template_items/" + this.props.activity + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({perspectives: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadPerspectivesFromServer();
        setInterval(()=>this.loadPerspectivesFromServer(),
                     this.props.pollInterval);
    }

    //take care  of no perspective case
    render() {
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

                    <h3>{this.props.name}</h3>
                    {perspectiveNodes}
                </div>
            )
        }

    }

    mapPerspectives(perspective) {
        return <PerspectiveComponent activity={this.props.activity} perspective={perspective.id} name={perspective.name}
                                     activityName={this.props.name} key={perspective.id} pollInterval={500}/>;
    }
}

class ActivityGridComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {activities: []};
    }

    loadActivitiesFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_activities/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({activities: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadActivitiesFromServer();
        setInterval(() => this.loadActivitiesFromServer(),
            this.props.pollInterval);
    }

    render() {
        if (this.state.activities) {
            const containerStyle = {
                marginLeft: "15px",
                marginRight: "15px"
            };
            var perspectiveGrids = this.state.activities.map(function (activity) {
                return <PerspectiveGridComponent activity={activity.id} name={activity.title} key={activity.id} pollInterval={5000}/>

            });
            return (

                <div className="container-fluid" style={containerStyle}>
                    {perspectiveGrids}
                </div>
            )
        }

    }
}
ReactDOM.render(<ActivityGridComponent pollInterval={5000}/>, document.getElementById("container"));



