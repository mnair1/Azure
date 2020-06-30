var AWS = require('aws-sdk');
// Set region
AWS.config.update({region: 'us-east-1'});

var params = {
  Message: 'ALERT - A new user connection was initiated on the server. Since this is off-period this may be a hacking attempt.', /* required */
  TopicArn: 'arn:aws:sns:us-east-1:956630041263:alert'
};


console.log('Loading function');

exports.handler = function(event, context) {
    //console.log(JSON.stringify(event, null, 2));
    event.Records.forEach(function(record) {
        // Kinesis data is base64 encoded so decode here
        var payload = new Buffer(record.kinesis.data, 'base64').toString('ascii');
        console.log('Decoded payload:', payload);

        var pos = payload.indexOf("New session");
        console.log('pos:', pos);
       if (pos > 0) {
         {
             var publishTextPromise = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params).promise();
             publishTextPromise.then(
            function(data) {
              console.log("Message ${params.Message} send sent to the topic ${params.TopicArn}");
              console.log("MessageID is " + data.MessageId);
            }).catch(
              function(err) {
              console.error(err, err.stack);
           });
         }
       }
        });
        
};


