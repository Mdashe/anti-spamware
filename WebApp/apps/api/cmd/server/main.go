package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/Mdashe/anti-spamware/apps/api/internal/config"
	"github.com/Mdashe/anti-spamware/apps/api/internal/db"
	"github.com/Mdashe/anti-spamware/apps/api/internal/handler"
	"github.com/Mdashe/anti-spamware/apps/api/internal/repository"
)

func main() {
	cfg := config.Load()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	pool, err := db.Connect(ctx, cfg.DatabaseURL)
	cancel()
	if err != nil {
		log.Fatalf("database: %v", err)
	}
	defer pool.Close()

	repo := repository.New(pool)
	h := handler.New(repo)

	mux := http.NewServeMux()
	h.Register(mux)

	addr := fmt.Sprintf(":%s", cfg.Port)
	server := &http.Server{
		Addr:    addr,
		Handler: mux,
	}

	go func() {
		log.Printf("api listening on http://localhost%s", addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer shutdownCancel()
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Printf("shutdown: %v", err)
	}
}
