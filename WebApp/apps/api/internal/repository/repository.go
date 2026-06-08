package repository

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	pool *pgxpool.Pool
}

func New(pool *pgxpool.Pool) *Repository {
	return &Repository{pool: pool}
}

type ProcResult struct {
	Status  int
	ID      *int
	Message string
}

func scanID(id *int32) *int {
	if id == nil {
		return nil
	}
	v := int(*id)
	return &v
}

func (r *Repository) InsertUser(ctx context.Context, email, name string) (ProcResult, error) {
	var status int
	var userID *int32
	var message string

	err := r.pool.QueryRow(ctx,
		`SELECT status, user_id, message FROM fn_user_insert($1, $2)`,
		email, name,
	).Scan(&status, &userID, &message)
	if err != nil {
		return ProcResult{}, err
	}

	return ProcResult{Status: status, ID: scanID(userID), Message: message}, nil
}

func (r *Repository) InsertEmail(ctx context.Context, userID, accountID int, providerEmailID, threadID, subject, sender string, recipients []string, snippet string, receivedAt time.Time, cachedBody string) (ProcResult, error) {
	var status int
	var emailID *int32
	var message string

	err := r.pool.QueryRow(ctx,
		`SELECT status, email_id, message FROM fn_email_insert($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
		userID, accountID, providerEmailID, threadID, subject, sender, recipients, snippet, receivedAt, cachedBody,
	).Scan(&status, &emailID, &message)
	if err != nil {
		return ProcResult{}, err
	}

	return ProcResult{Status: status, ID: scanID(emailID), Message: message}, nil
}

func (r *Repository) InsertClassification(ctx context.Context, emailID int, label string, confidence float64, modelVersion, source string) (ProcResult, error) {
	var status int
	var classificationID *int32
	var message string

	err := r.pool.QueryRow(ctx,
		`SELECT status, classification_id, message FROM fn_classification_insert($1, $2, $3, $4, $5)`,
		emailID, label, confidence, modelVersion, source,
	).Scan(&status, &classificationID, &message)
	if err != nil {
		return ProcResult{}, err
	}

	return ProcResult{Status: status, ID: scanID(classificationID), Message: message}, nil
}

func (r *Repository) InsertRule(ctx context.Context, userID int, name, conditionType, conditionValue, action string, enabled bool) (ProcResult, error) {
	var status int
	var ruleID *int32
	var message string

	err := r.pool.QueryRow(ctx,
		`SELECT status, rule_id, message FROM fn_rule_insert($1, $2, $3, $4, $5, $6)`,
		userID, name, conditionType, conditionValue, action, enabled,
	).Scan(&status, &ruleID, &message)
	if err != nil {
		return ProcResult{}, err
	}

	return ProcResult{Status: status, ID: scanID(ruleID), Message: message}, nil
}

func (r *Repository) Ping(ctx context.Context) error {
	return r.pool.Ping(ctx)
}
